from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
import logging

# Конфигурация логирования
logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет сообщение, когда выполняется команда /start."""
    user = update.effective_user
    
    # Отправляем приветственное сообщение в формате HTML
    await update.message.reply_html(
        f"Здравствуйте, **{user.first_name}!**\n\n"
        "Я ваш персональный бот RAG (Retrieval-Augmented Generation).\n\n"
        "Задайте мне технический вопрос. Я найду релевантную информацию в интернете и предоставлю вам развернутый ответ, включая источники.\n"
        "Например, введите: `Что такое механизм ** в Python?`",
    )

# --- Конфигурация Обработчиков ---

# Объект CommandHandler, который связывает команду /start с функцией start_command
start_handler = CommandHandler("start", start_command)

# Список всех обработчиков, предоставляемых этим модулем
HANDLERS = [start_handler]