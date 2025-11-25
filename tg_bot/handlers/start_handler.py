from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from tg_bot.handlers.base_handler import BaseHandler

class StartHandler(BaseHandler):
    async def start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.message.from_user
        await update.message.reply_text(
            f'Привет {user.first_name}! Я бот, работающий c MistralAI!'
        )

    def register_handlers(self, application):
        application.add_handler(
            CommandHandler('start', self.start_handler)
        )