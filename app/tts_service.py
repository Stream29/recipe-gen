import os
import base64
import dashscope
from dashscope.audio.qwen_tts import SpeechSynthesizer

class TTSService:
    """
    A class to convert text to speech using the dashscope TTS API.
    """
    
    def __init__(self, api_key=None):
        """
        Initialize the TTSService with an API key.
        
        Args:
            api_key (str, optional): The API key for dashscope. If None, it will use the environment variable.
        """
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required. Set it as an argument or as DASHSCOPE_API_KEY environment variable.")
    
    def text_to_speech(self, text, voice="Ethan", stream=False):
        """
        Convert text to speech.
        
        Args:
            text (str): The text to convert to speech.
            voice (str, optional): The voice to use. Defaults to "Ethan".
            stream (bool, optional): Whether to stream the audio. Defaults to False.
            
        Returns:
            If stream=False, returns a URL to the audio file.
            If stream=True, returns a generator yielding audio chunks.
        """
        if stream:
            return self._stream_tts(text, voice)
        else:
            return self._tts(text, voice)
    
    def _tts(self, text, voice):
        """
        Convert text to speech and return a URL to the audio file.
        
        Args:
            text (str): The text to convert to speech.
            voice (str): The voice to use.
            
        Returns:
            str: URL to the audio file.
        """
        response = SpeechSynthesizer.call(
            model="qwen-tts",
            api_key=self.api_key,
            text=text,
            voice=voice,
        )
        
        if hasattr(response, 'output') and hasattr(response.output, 'audio') and 'url' in response.output.audio:
            return response.output.audio["url"]
        else:
            raise Exception("Failed to generate speech")
    
    def _stream_tts(self, text, voice):
        """
        Stream text to speech conversion.
        
        Args:
            text (str): The text to convert to speech.
            voice (str): The voice to use.
            
        Returns:
            generator: A generator yielding audio chunks.
        """
        responses = SpeechSynthesizer.call(
            model="qwen-tts",
            api_key=self.api_key,
            text=text,
            voice=voice,
            stream=True
        )
        
        for chunk in responses:
            if hasattr(chunk, 'output') and hasattr(chunk.output, 'audio') and 'data' in chunk.output.audio:
                audio_string = chunk.output.audio["data"]
                wav_bytes = base64.b64decode(audio_string)
                yield wav_bytes
            else:
                raise Exception("Failed to generate speech chunk")
    
    def text_to_speech_file(self, text, output_path, voice="Ethan"):
        """
        Convert text to speech and save it to a file.
        
        Args:
            text (str): The text to convert to speech.
            output_path (str): The path to save the audio file.
            voice (str, optional): The voice to use. Defaults to "Ethan".
            
        Returns:
            str: The path to the saved audio file.
        """
        import requests
        
        audio_url = self._tts(text, voice)
        
        try:
            response = requests.get(audio_url)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
                
            return output_path
        except Exception as e:
            raise Exception(f"Failed to download audio file: {str(e)}")