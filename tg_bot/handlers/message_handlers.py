# RAG_product/tg_bot/handlers/message_handlers.py

from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
import logging

# Importez ici la logique RAG réelle (votre agent)
# L'importation de 'MultiAgentBot' est juste un placeholder pour montrer où l'utiliser
# from tg_bot.bot_core import MultiAgentBot

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_rag_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gère un message texte et utilise le modèle RAG pour répondre."""
    user_query = update.message.text
    chat_id = update.effective_chat.id

    logger.info(f"Requête reçue de {update.effective_user.first_name} : {user_query}")
    
    # 1. Accuser réception de la requête
    await update.message.reply_text("J'ai reçu votre question. Laissez-moi chercher la meilleure réponse dans mes documents...")

    # --- LOGIQUE RAG / AGENT ICI ---
    # Ici, vous intégreriez la logique de votre 'MultiAgentBot' ou de votre pipeline RAG.
    
    # Exemple de placeholder de la réponse RAG
    try:
        # Supposons que votre pipeline RAG est accessible via le contexte de l'application
        # self.rag_agent = context.bot_data.get("rag_agent")
        # if self.rag_agent:
        #     rag_response = self.rag_agent.process_query(user_query)
        # else:
        #     rag_response = "Erreur : Agent RAG non initialisé."
        
        # Réponse simulée pour l'exemple :
        rag_response = f"**Réponse RAG pour :** '{user_query}'\n\n"
        rag_response += "Le modèle RAG combine la recherche de documents (Retrieval) et la génération de texte (Generation) par un grand modèle de langage pour fournir des réponses précises et contextualisées."

    except Exception as e:
        logger.error(f"Erreur lors du traitement RAG : {e}")
        rag_response = "Désolé, une erreur s'est produite lors de la recherche d'informations."
        
    # 2. Envoyer la réponse finale à l'utilisateur
    await context.bot.send_message(
        chat_id=chat_id,
        text=rag_response,
        parse_mode="Markdown" # Permet l'utilisation du gras (**)
    )


# --- Configuration des Handlers ---

# Ce handler filtre TOUS les messages qui sont du texte, mais NE SONT PAS des commandes.
rag_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_rag_query)

# Pour l'intégration dans bot_core.py, vous pouvez exporter la liste des handlers
HANDLERS = [rag_handler]