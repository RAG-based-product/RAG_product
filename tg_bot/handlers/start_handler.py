# RAG_product/tg_bot/handlers/start_handler.py

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
import logging

# Конфигурация логирования
logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envoie un message lorsque la commande /start est émise."""
    user = update.effective_user
    
    await update.message.reply_html(
        f"👋 Bonjour, **{user.first_name}!**\n\n"
        "Je suis votre Bot RAG (Retrieval-Augmented Generation) personnel.\n\n"
        "Posez-moi une question technique. Je vais chercher des informations pertinentes et vous fournir une réponse.\n"
        "Essayez de taper : `Que signifie l'opérateur ** en Python ?`",
    )

# --- Configuration des Handlers ---

# Объект CommandHandler, который НЕ ДОЛЖЕН ВЫЗЫВАТЬСЯ как функция в bot_core.py
start_handler = CommandHandler("start", start_command)

# Список всех обработчиков, предоставляемых этим модулем
HANDLERS = [start_handler]