import os
import requests
import dashscope

from dashscope.api_entities.dashscope_response import TextToSpeechResponse
from dashscope.audio.qwen_tts import SpeechSynthesizer

text: str = "那我来给大家推荐一款T恤，这款呢真的是超级好看，这个颜色呢很显气质，而且呢也是搭配的绝佳单品，大家可以闭眼入，真的是非常好看，对身材的包容性也很好，不管啥身材的宝宝呢，穿上去都是很好看的。推荐宝宝们下单哦。"
response: TextToSpeechResponse = dashscope.audio.qwen_tts.SpeechSynthesizer.call(
    model="qwen-tts",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    text=text,
    voice="Cherry",
)
audio_url: str = response.output.audio["url"]
save_path: str = "downloaded_audio.wav"  # 自定义保存路径

try:
    response: requests.Response = requests.get(audio_url)
    response.raise_for_status()  # 检查请求是否成功
    with open(save_path, 'wb') as f:
        f.write(response.content)
    print(f"音频文件已保存至：{save_path}")
except Exception as e:
    print(f"下载失败：{str(e)}")
