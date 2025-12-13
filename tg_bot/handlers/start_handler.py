# RAG_product/tg_bot/handlers/start_handler.py

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
import logging

# Configurez le logging pour voir les messages d'activité
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envoie un message lorsque la commande /start est émise."""
    user = update.effective_user
    
    # Utilisez le nom d'utilisateur pour personnaliser l'accueil
    await update.message.reply_html(
        f"👋 Bonjour, **{user.first_name}!**\n\n"
        "Je suis votre Bot RAG (Retrieval-Augmented Generation) personnel.\n\n"
        "Posez-moi une question sur mes documents. Je vais chercher la réponse et vous la fournir.\n"
        "Essayez de taper : `Qu'est-ce que le modèle RAG ?`",
        # Le 'reply_markup' pourrait inclure des boutons si nécessaire
    )

# --- Configuration des Handlers ---

# Un 'handler' (gestionnaire) relie une commande (comme /start) à une fonction (start_command)
start_handler = CommandHandler("start", start_command)

# Pour l'intégration dans bot_core.py, vous pouvez exporter la liste des handlers
HANDLERS = [start_handler]