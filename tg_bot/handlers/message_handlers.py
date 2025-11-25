from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

from tg_bot.handlers.base_handler import BaseHandler

class MessageHandlers(BaseHandler):
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.chat.send_action(action="typing")
        response = await self.bot.process_user_message(update, context)
        await update.message.reply_text(response)
    
    def register_handlers(self, application):
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message)
        )




