import os
import base64
import dashscope
from dashscope.audio.qwen_tts import SpeechSynthesizer
from app.llm_logger import LLMLogger

class TTSService:
    """
    A class to convert text to speech using the dashscope TTS API.
    """

    # Maximum token limit for the TTS API (approximately 500 characters)
    MAX_TOKEN_LENGTH = 500

    def __init__(self, api_key=None, log_dir="logs"):
        """
        Initialize the TTSService with an API key.

        Args:
            api_key (str, optional): The API key for dashscope. If None, it will use the environment variable.
            log_dir (str, optional): Directory to store logs. Defaults to "logs".
        """
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required. Set it as an argument or as DASHSCOPE_API_KEY environment variable.")

        # Initialize logger
        self.logger = LLMLogger(log_dir=log_dir)

    def _split_text(self, text):
        """
        Split text into segments based on newlines and maximum token length.

        Args:
            text (str): The text to split.

        Returns:
            list: A list of text segments.
        """
        # First split by newlines
        segments = []
        lines = text.split('\n')

        current_segment = ""
        for line in lines:
            # If adding this line would exceed the limit, add the current segment to the list
            # and start a new segment with this line
            if len(current_segment) + len(line) > self.MAX_TOKEN_LENGTH:
                if current_segment:
                    segments.append(current_segment)

                # If the line itself is longer than the limit, split it further
                if len(line) > self.MAX_TOKEN_LENGTH:
                    # Split the line into chunks of MAX_TOKEN_LENGTH
                    for i in range(0, len(line), self.MAX_TOKEN_LENGTH):
                        segments.append(line[i:i + self.MAX_TOKEN_LENGTH])
                    current_segment = ""
                else:
                    current_segment = line
            else:
                # Add this line to the current segment
                if current_segment:
                    current_segment += "\n" + line
                else:
                    current_segment = line

        # Add the last segment if it's not empty
        if current_segment:
            segments.append(current_segment)

        return segments

    def text_to_speech(self, text, voice="Ethan", stream=False):
        """
        Convert text to speech.

        Args:
            text (str): The text to convert to speech.
            voice (str, optional): The voice to use. Defaults to "Ethan".
            stream (bool, optional): Whether to stream the audio. Defaults to False.

        Returns:
            If stream=False, returns a list of URLs to the audio files.
            If stream=True, returns a generator yielding audio chunks.
        """
        # Split text into segments
        segments = self._split_text(text)

        if stream:
            return self._stream_tts_segments(segments, voice)
        else:
            return self._tts_segments(segments, voice)

    def _tts_segments(self, segments, voice):
        """
        Convert text segments to speech and return URLs to the audio files.

        Args:
            segments (list): List of text segments to convert to speech.
            voice (str): The voice to use.

        Returns:
            list: List of URLs to the audio files.
        """
        audio_urls = []

        for segment in segments:
            if not segment.strip():
                continue

            url = self._tts_single(segment, voice)
            audio_urls.append(url)

        return audio_urls

    def _tts_single(self, text, voice):
        """
        Convert a single text segment to speech and return a URL to the audio file.

        Args:
            text (str): The text segment to convert to speech.
            voice (str): The voice to use.

        Returns:
            str: URL to the audio file.
        """
        # Log the input
        self.logger.log_tts(input_text=text, voice=voice, model="qwen-tts")

        response = SpeechSynthesizer.call(
            model="qwen-tts",
            api_key=self.api_key,
            text=text,
            voice=voice,
        )

        if hasattr(response, 'output') and hasattr(response.output, 'audio') and 'url' in response.output.audio:
            url = response.output.audio["url"]

            # Log the output
            self.logger.log_tts(input_text=text, output_url=url, voice=voice, model="qwen-tts")

            return url
        else:
            # Log the error
            self.logger.log_tts(
                input_text=text, 
                output_url=None, 
                voice=voice, 
                model="qwen-tts"
            )

            raise Exception("Failed to generate speech")

    def _stream_tts_segments(self, segments, voice):
        """
        Stream text segments to speech conversion.

        Args:
            segments (list): List of text segments to convert to speech.
            voice (str): The voice to use.

        Returns:
            generator: A generator yielding audio chunks.
        """
        for segment in segments:
            if not segment.strip():
                continue

            yield from self._stream_tts_single(segment, voice)

    def _stream_tts_single(self, text, voice):
        """
        Stream a single text segment to speech conversion.

        Args:
            text (str): The text segment to convert to speech.
            voice (str): The voice to use.

        Returns:
            generator: A generator yielding audio chunks.
        """
        # Log the input
        self.logger.log_tts(input_text=text, voice=voice, model="qwen-tts")

        responses = SpeechSynthesizer.call(
            model="qwen-tts",
            api_key=self.api_key,
            text=text,
            voice=voice,
            stream=True
        )

        total_bytes = 0
        try:
            for chunk in responses:
                if hasattr(chunk, 'output') and hasattr(chunk.output, 'audio') and 'data' in chunk.output.audio:
                    audio_string = chunk.output.audio["data"]
                    wav_bytes = base64.b64decode(audio_string)
                    total_bytes += len(wav_bytes)
                    yield wav_bytes
                else:
                    # Log the error
                    self.logger.log_tts(
                        input_text=text, 
                        output_data=None, 
                        voice=voice, 
                        model="qwen-tts"
                    )
                    raise Exception("Failed to generate speech chunk")

            # Log the output after streaming is complete
            self.logger.log_tts(
                input_text=text, 
                output_data=b'streaming_data', 
                voice=voice, 
                model="qwen-tts"
            )
        except Exception as e:
            # Log any exceptions
            self.logger.log_tts(
                input_text=text, 
                output_data=None, 
                voice=voice, 
                model="qwen-tts"
            )
            raise e

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
        import wave
        import io
        import os

        # Split text into segments
        segments = self._split_text(text)
        audio_urls = self._tts_segments(segments, voice)

        # If there's only one segment, download it directly
        if len(audio_urls) == 1:
            try:
                response = requests.get(audio_urls[0])
                response.raise_for_status()

                with open(output_path, 'wb') as f:
                    f.write(response.content)

                return output_path
            except Exception as e:
                raise Exception(f"Failed to download audio file: {str(e)}")

        # If there are multiple segments, combine them into a single WAV file
        try:
            # Create a list to store audio data
            audio_data_list = []

            # Download each audio file
            for url in audio_urls:
                response = requests.get(url)
                response.raise_for_status()
                audio_data_list.append(response.content)

            # Combine audio files
            with wave.open(output_path, 'wb') as outfile:
                # Use the first file to set parameters
                with wave.open(io.BytesIO(audio_data_list[0]), 'rb') as first_file:
                    params = first_file.getparams()
                    outfile.setparams(params)

                    # Write the first file's frames
                    outfile.writeframes(first_file.readframes(first_file.getnframes()))

                # Append the rest of the files
                for audio_data in audio_data_list[1:]:
                    with wave.open(io.BytesIO(audio_data), 'rb') as infile:
                        outfile.writeframes(infile.readframes(infile.getnframes()))

            return output_path
        except Exception as e:
            # Clean up the output file if it exists
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except:
                    pass
            raise Exception(f"Failed to combine audio files: {str(e)}")
