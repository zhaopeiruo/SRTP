import os
from dotenv import load_dotenv

# 从 .env 文件加载环境变量
load_dotenv()

class Config:
    API_KEY = os.getenv("LLM_API_KEY")
    BASE_URL = os.getenv("LLM_BASE_URL")
    MODEL_NAME = os.getenv("LLM_MODEL", "gpt-4o")

    @staticmethod
    def validate():
        if not Config.API_KEY:
            raise ValueError("未在环境变量中设置 LLM_API_KEY。")
        if not Config.BASE_URL:
            raise ValueError("未在环境变量中设置 LLM_BASE_URL。")
