from langchain_mistralai.chat_models import ChatMistralAI
from typing import List, Dict, Any
from dotenv import load_dotenv
import os
import logging
import sys
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class MistralLLMClient: 

    def __init__(self):

        load_dotenv() 

        self.API_KEY = os.getenv("MISTRAL_API_KEY") 
        
        # если нужно поддержать название 'mistral' как во второй версии:
        if not self.API_KEY:
            self.API_KEY = os.getenv("mistral")

        # 
        if not self.API_KEY:
            raise ValueError("MISTRAL_API_KEY (или 'mistral') не найдены в переменных окружения!")
        else:
            logger.info("MISTRAL_API_KEY успешно загружен!")
    
    async def generate(self, messages: List[Dict[str, Any]], model: str = "mistral-small-latest", temperature: float = 0.7) -> str:
        """
        Генерация одного ответа Mistral.
        """
        try:
            llm = ChatMistralAI(
                mistral_api_key=self.API_KEY,
                model_name=model,
                temperature=temperature,
            )

            result = await llm.ainvoke(messages)
            return result.content
        except Exception as e:
            logger.error(f"Ошибка API LLM Mistral: {str(e)}")
            raise Exception(f"Ошибка API LLM Mistral: {str(e)}")
