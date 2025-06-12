import os
import json
import logging
import datetime
from pathlib import Path

class LLMLogger:
    """
    A utility class for logging LLM API calls.
    """
    
    def __init__(self, log_dir="logs"):
        """
        Initialize the LLMLogger.
        
        Args:
            log_dir (str, optional): Directory to store logs. Defaults to "logs".
        """
        self.log_dir = log_dir
        
        # Create logs directory if it doesn't exist
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(self.log_dir, "llm_api.log")),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("LLMLogger")
    
    def log_text_generation(self, input_data, output_data, model="qwen-plus"):
        """
        Log text generation API calls.
        
        Args:
            input_data: The input data sent to the API.
            output_data: The output data received from the API.
            model (str, optional): The model used for generation. Defaults to "qwen-plus".
        """
        timestamp = datetime.datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "type": "text_generation",
            "model": model,
            "input": input_data,
            "output": output_data
        }
        
        # Log to file
        log_file = os.path.join(self.log_dir, f"text_generation_{datetime.datetime.now().strftime('%Y%m%d')}.json")
        self._append_to_json_log(log_file, log_entry)
        
        # Log to standard logger
        self.logger.info(f"Text Generation API Call - Model: {model}")
    
    def log_tts(self, input_text, output_url=None, output_data=None, voice="Ethan", model="qwen-tts"):
        """
        Log text-to-speech API calls.
        
        Args:
            input_text (str): The input text sent to the API.
            output_url (str, optional): The URL of the generated audio.
            output_data (bytes, optional): The raw audio data for streaming responses.
            voice (str, optional): The voice used for TTS. Defaults to "Ethan".
            model (str, optional): The model used for TTS. Defaults to "qwen-tts".
        """
        timestamp = datetime.datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "type": "tts",
            "model": model,
            "voice": voice,
            "input": input_text,
        }
        
        # Add output information
        if output_url:
            log_entry["output_url"] = output_url
        if output_data:
            log_entry["output_size"] = len(output_data) if output_data else 0
        
        # Log to file
        log_file = os.path.join(self.log_dir, f"tts_{datetime.datetime.now().strftime('%Y%m%d')}.json")
        self._append_to_json_log(log_file, log_entry)
        
        # Log to standard logger
        self.logger.info(f"TTS API Call - Model: {model}, Voice: {voice}")
    
    def _append_to_json_log(self, log_file, log_entry):
        """
        Append a log entry to a JSON log file.
        
        Args:
            log_file (str): Path to the log file.
            log_entry (dict): The log entry to append.
        """
        # Read existing logs if file exists
        existing_logs = []
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    existing_logs = json.load(f)
            except json.JSONDecodeError:
                # If the file is corrupted, start with an empty list
                existing_logs = []
        
        # Append new log entry
        existing_logs.append(log_entry)
        
        # Write back to file
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(existing_logs, f, ensure_ascii=False, indent=2)