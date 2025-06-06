import os
import dashscope
import pyaudio
import time
import base64
import numpy as np

p = pyaudio.PyAudio()
# 创建音频流
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=24000,
                output=True)


text = "你好啊，我是通义千问"
responses = dashscope.audio.qwen_tts.SpeechSynthesizer.call(
    model="qwen-tts",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    text=text,
    voice="Ethan",
    stream=True
)
for chunk in responses:
    audio_string = chunk["output"]["audio"]["data"]
    wav_bytes = base64.b64decode(audio_string)
    audio_np = np.frombuffer(wav_bytes, dtype=np.int16)
    # 直接播放音频数据
    stream.write(audio_np.tobytes())

time.sleep(0.8)
# 清理资源
stream.stop_stream()
stream.close()
p.terminate()