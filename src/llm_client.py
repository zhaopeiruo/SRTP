from openai import OpenAI
from src.config import Config
import base64

class LLMClient:
    def __init__(self):
        Config.validate()
        self.client = OpenAI(
            api_key=Config.API_KEY,
            base_url=Config.BASE_URL
        )
        self.model = Config.MODEL_NAME

    def chat_completion(self, messages, temperature=0.7):
        """
        向 LLM 发送聊天补全请求。
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"调用 LLM 时出错: {e}")
            raise e

    def encode_image(self, image_path):
        """
        将图片编码为 base64 字符串。
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
