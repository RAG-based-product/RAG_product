from langchain_mistralai.chat_models import ChatMistralAI
from typing import List, Dict
from dotenv import load_dotenv
import os
from models.base_llm_client import BaseLLMClient

class MistralLLMClient(BaseLLMClient):
    def __init__(self):
        load_dotenv()
        self.API_KEY = os.getenv("MISTRAL_API_KEY")
        if not self.API_KEY:
            raise ValueError("MISTRAL_API_KEY not found!")
        print("API key loaded successfully!")

<<<<<<< HEAD
        self.API_KEY = None
        load_dotenv(".env")
        API_KEY = os.environ.get("mistral")

        if not API_KEY:
            raise ValueError("MISTRAL_API_KEY not found!")
        else:
            print("API key loaded successfully!")
            self.API_KEY = API_KEY
    
=======
>>>>>>> main
    async def generate(self, messages: List[Dict], model: str = "mistral-small-latest", temperature: float = 0.7) -> str:
        try:
            llm = ChatMistralAI(
                mistral_api_key=self.API_KEY,
                model_name=model,
                temperature=temperature,
            )
            result = await llm.ainvoke(messages)
            return result.content
        except Exception as e:
            raise Exception(f"LLM API error: {str(e)}")
