# RAG_product/tg_bot/bot_core.py

from typing import List, Optional
import logging
from telegram.ext import CommandHandler, filters, MessageHandler as TgMessageHandler
from telegram.ext import ContextTypes, Application
from telegram import Update

# Импорты ваших модулей
from tg_bot.handlers.message_handlers import MessageHandler as BotMessageHandler
from tg_bot.handlers.start_handler import start_handler 
from models.base_llm_client import BaseLLMClient
from web_search.base_web_search_engine import BaseWebSearchEngine
from models.prompts import get_prompt
from tg_bot.utils import get_application

logger = logging.getLogger(__name__)

class MultiAgentBot:
    def __init__(self, llm: BaseLLMClient | None, web_search_engine: BaseWebSearchEngine | None):
        
        self.application: Application = get_application()
        self.llm = llm
        self.web_search_engine = web_search_engine
        
        # Инициализируем все обработчики
        self.handlers = [
            # 1. Custom MessageHandler
            BotMessageHandler(self), 
            
            # 2. CommandHandler: Передается как готовый объект (без скобок)
            start_handler, 
        ]
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Регистрирует обработчики в приложении Telegram."""
        for handler in self.handlers:
            if hasattr(handler, 'register_handlers'):
                # Для кастомных обработчиков (BotMessageHandler)
                handler.register_handlers(self.application)
            else:
                # Для стандартных объектов Telegram Handler (CommandHandler, MessageHandler)
                self.application.add_handler(handler) 
    
    # 🚨 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Добавлен 'async'
    async def process_user_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """Основная логика RAG. Вызывается из MessageHandler."""
        user_message = update.message.text
        
        logger.info(f"Запуск RAG для запроса: {user_message[:50]}...")
        
        # 1. RETRIEVAL/CONTEXT
        try:
            # Предполагаем, что get_prompt синхронный, но может вызывать Tavily, который должен быть awaitable
            # Вам нужно будет проверить, требует ли get_prompt await
            prompt = get_prompt(user_message, self.web_search_engine)
        except Exception as e:
            logger.error(f"Ошибка при получении контекста (Tavily): {e}")
            return "Une erreur est survenue lors de la recherche d'informations. Veuillez vérifier les logs."

        # 2. GENERATION
        if self.llm:
            # 🚨 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Добавлен 'await' перед вызовом асинхронного метода
            ans = await self.llm.generate(messages=prompt) 
        else:
            ans = "Erreur : LLM n'est pas initialisé."
            
        return ans