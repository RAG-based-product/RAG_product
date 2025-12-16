from typing import List
from telegram.ext import MessageHandler as TgMessageHandler, filters
from telegram.ext import ContextTypes
from telegram import Update
import logging
# Импортирование модели Source для подсказок типов
from models.prompts import Source 

logger = logging.getLogger(__name__)

class MessageHandler:
    """
    Управляет текстовыми сообщениями, запускает RAG-пайплайн и отображает ответ,
    а также источники.
    """
    def __init__(self, bot_instance):
        self.bot = bot_instance

    async def _callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Асинхронный метод обратного вызова для обработки сообщения пользователя.
        """
        user_message = update.message.text
        logger.info(f"Получено сообщение от {update.effective_user.first_name}: {user_message}")

        final_response: str
        parse_mode: str | None = None

        try:
            # Получение кортежа (ответ LLM, список источников)
            llm_response, sources = await self.bot.process_user_message(update, context) 
            
            # --- 1. Форматирование источников ---
            if sources:
                # Используем **Sources:** для выделения секции источников
                source_links = "\n\n**Источники:**\n"
                # Ограничиваемся 3 источниками, чтобы не перегружать ответ
                for i, source in enumerate(sources[:3]): 
                    # Используем режим HTML для форматирования ссылки: <a href='URL'>Заголовок</a>
                    source_links += f"{i+1}. <a href='{source.url}'>{source.title}</a>\n"
                
                final_response = f"{llm_response}{source_links}"
                parse_mode = "HTML" # Устанавливаем режим парсинга HTML
            else:
                final_response = llm_response
                parse_mode = None

        except Exception as e:
            logger.error(f"Критическая ошибка в RAG-пайплайне: {e}", exc_info=True)
            final_response = "К сожалению, при обработке вашего запроса произошла критическая внутренняя ошибка."
            parse_mode = None

        # Отправка ответа с учетом соответствующего режима парсинга (HTML или None)
        await update.message.reply_text(final_response, parse_mode=parse_mode)

    def register_handlers(self, application):
        """Регистрирует обработчик сообщений в приложении Telegram."""
        application.add_handler(
            TgMessageHandler(
                filters.TEXT & (~filters.COMMAND), # Фильтр: текст, не команды
                self._callback
            )
        )