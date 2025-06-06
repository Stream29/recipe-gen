import os
from dashscope import Generation

messages: list = [
    {'role': 'system', 'content': 'you are a helpful assistant'},
    {'role': 'user', 'content': '你是谁？'}]
responses = Generation.call(
    # 若没有配置环境变量，请用阿里云百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    model="qwen-plus",  # 此处以qwen-plus为例，您可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    messages=messages,
    result_format='message',
    stream=True,
    # 增量式流式输出
    incremental_output=True,
    # Qwen3模型通过enable_thinking参数控制思考过程（开源版默认True，商业版默认False）
    # 使用Qwen3开源版模型时，若未启用流式输出，请将下行取消注释，否则会报错
    # enable_thinking=False
)
full_content = ""
print("流式输出内容为：")
for response in responses:
    full_content += response.output.choices[0].message.content
    print(response.output.choices[0].message.content)
print(f"完整内容为：{full_content}")
