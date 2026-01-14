from typing import List, Optional, Tuple
import logging
from telegram.ext import CommandHandler
from telegram.ext import ContextTypes, Application
from telegram import Update 
from tg_bot.handlers.message_handlers import MessageHandler as BotMessageHandler
from tg_bot.handlers.start_handler import start_handler 
from models.base_llm_client import BaseLLMClient
from web_search.base_web_search_engine import BaseWebSearchEngine
from models.prompts import get_prompt, Source # 🚨 Импорт get_prompt и Source
from tg_bot.utils import get_application

logger = logging.getLogger(__name__)

class MultiAgentBot:
    def __init__(self, llm: BaseLLMClient | None, web_search_engine: BaseWebSearchEngine | None):
        
        self.application: Application = get_application()
        self.llm = llm
        self.web_search_engine = web_search_engine
        
        # Инициализация обработчиков (Handlers)
        self.handlers = [
            BotMessageHandler(self), # Управляет текстовыми сообщениями и вызывает process_user_message
            start_handler,           # Управляет командой /start (объект CommandHandler)
        ]
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Регистрирует обработчики в приложении Telegram."""
        for handler in self.handlers:
            # Если это кастомный обработчик с register_handlers()
            if hasattr(handler, 'register_handlers'):
                handler.register_handlers(self.application)
            # Если это стандартный объект (напр., CommandHandler)
            else:
                self.application.add_handler(handler) 
    
    # Асинхронный метод, который возвращает ответ и источники
    async def process_user_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Tuple[str, List[Source]]:
        """Реализует пайплайн RAG (Retrieval-Augmented Generation)."""
        user_message = update.message.text
        
        # RETRIEVAL/КОНТЕКСТ
        try:
            # Получение промпта И списка источников
            final_prompt, sources = get_prompt(user_message, self.web_search_engine) 
        except Exception as e:
            logger.error(f"Ошибка при получении промпта: {e}")
            # Возврат ошибки и пустого списка источников
            return "Произошла ошибка при подготовке запроса (проверьте Tavily).", []

        # GENERATION
        ans = "Ошибка: Модель LLM не инициализирована."
        if self.llm:
            try:
                # Асинхронный вызов модели LLM
                ans = await self.llm.generate(messages=final_prompt) 
            except Exception as e:
                logger.error(f"Ошибка при генерации LLM: {e}")
                ans = "Модель LLM не смогла сгенерировать ответ."
        
        # ЫВОД: Возврат ответа LLM и источников
        return ans, sources