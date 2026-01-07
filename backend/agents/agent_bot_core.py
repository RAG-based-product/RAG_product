# backend/agents/agent_bot_core.py
from typing import List, Tuple, Dict, Any
import logging
from agents.base_agent import BaseAgent
from models.base_llm_client import BaseLLMClient
from web_search.base_web_search_engine import BaseWebSearchEngine
from models.prompts import get_prompt, Source
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class AgentBot(BaseAgent):
    """
    Сервис для обработки RAG-запросов.
    Инкапсулирует логику Retrieval-Augmented Generation.
    """
    
    def __init__(
        self, 
        name: str, 
        llm_client: BaseLLMClient, 
        system_prompt: str,
        web_search_engine: BaseWebSearchEngine = None
    ):
        super().__init__(name=name, llm_client=llm_client, system_prompt=system_prompt)
        self.web_search_engine = web_search_engine

    async def process(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Обрабатывает запрос пользователя через RAG-пайплайн.
        
        Args:
            message: Сообщение пользователя
            context: Дополнительный контекст (опционально)
        
        Returns:
            Dict[str, Any]: {
                "answer": str - ответ LLM,
                "sources": List[Source] - список источников
            }
        """
        if context is None:
            context = {}
        
        # 1. RETRIEVAL/КОНТЕКСТ
        if not self.web_search_engine:
            logger.error("WebSearchEngine не инициализирован")
            return {
                "answer": "Ошибка: WebSearchEngine не настроен.",
                "sources": []
            }
        
        try:
            final_prompt, sources = get_prompt(message, self.web_search_engine)
        except Exception as e:
            logger.error(f"Ошибка при получении промпта: {e}")
            return {
                "answer": "Произошла ошибка при подготовке запроса (проверьте WebSearch).",
                "sources": []
            }
        
        # 2. GENERATION
        # Используем метод из BaseAgent, который добавляет system_prompt
        try:
            # Преобразуем final_prompt (строка) в формат для _call_llm
            # Если final_prompt уже строка, оборачиваем в сообщение
            if isinstance(final_prompt, str):
                messages = [{"role": "user", "content": final_prompt}]
            else:
                messages = final_prompt
            
            ans = await self._call_llm(messages)
        except Exception as e:
            logger.error(f"Ошибка при генерации LLM: {e}")
            ans = "Модель LLM не смогла сгенерировать ответ."
        
        # 3. ВЫВОД
        return {
            "answer": ans,
            "sources": sources
        }