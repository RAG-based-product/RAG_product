from langchain_mistralai import ChatMistralAI

from typing import List, Dict
# from utils.config import Config
from dotenv import load_dotenv
import os

from models.base_llm_client import BaseLLMClient
class MistralLLMClient(BaseLLMClient):
    def __init__(self):
        self.API_KEY = None
        load_dotenv(".env")
        API_KEY = os.environ.get("mistral")

        if not API_KEY:
            raise ValueError("❌ MISTRAL_API_KEY not found!")
        else:
            print("✅ MISTRAL_API_KEY loaded successfully!")
            self.API_KEY = API_KEY
    
    async def generate(self, messages: List[Dict], model: str = "mistral-small-latest", temperature: float = 0.7) -> str:
        try:
            llm = ChatMistralAI(
                api_key = self.API_KEY,
                model=model,
                temperature=temperature,
            )
            result = llm.invoke(messages)
            return result.content

        except Exception as e:
            raise Exception(f"LLM API error: {str(e)}")