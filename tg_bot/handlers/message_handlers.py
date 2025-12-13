# RAG_product/tg_bot/handlers/message_handlers.py

from telegram.ext import MessageHandler as TgMessageHandler, filters
from telegram.ext import ContextTypes
from telegram import Update
import logging

logger = logging.getLogger(__name__)

class MessageHandler:
    """
    Кастомный обработчик для текстовых сообщений, который вызывает логику RAG
    из класса MultiAgentBot.
    """
    def __init__(self, bot_instance):
        self.bot = bot_instance

    async def _callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Метод, вызываемый при получении сообщения. 
        Должен быть асинхронным.
        """
        user_message = update.message.text
        logger.info(f"Получено сообщение от {update.effective_user.first_name}: {user_message}")

        # 🚨 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Добавлен 'await' перед вызовом асинхронного метода
        try:
            response_text = await self.bot.process_user_message(update, context) 
        except Exception as e:
            logger.error(f"Ошибка при обработке сообщения в RAG-пайплайне: {e}")
            response_text = "Désolé, une erreur interne s'est produite lors du traitement de votre demande."

        await update.message.reply_text(response_text)

    def register_handlers(self, application):
        """Регистрирует обработчик в Telegram Application."""
        application.add_handler(
            TgMessageHandler(
                filters.TEXT & (~filters.COMMAND), # Фильтр: текст, не команды
                self._callback                     # Callback-функция
            )
        )