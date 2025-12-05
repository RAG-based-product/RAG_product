from typing import List, Literal, Optional, Dict, Any
from pydantic import BaseModel
from mistralai import Mistral

import logging
from telegram.ext import CommandHandler, filters, MessageHandler

# from handlers.handlers import echo, start
from tg_bot.handlers.message_handlers import MessageHandlers
from tg_bot.handlers.start_handler import StartHandler
from models.base_llm_client import BaseLLMClient
from web_search.base_web_search_engine import BaseWebSearchEngine
from models.prompts import get_prompt
# from models.mistral_llm_client import MistralLLMClient
from tg_bot.utils import get_application

# Load environment variables


# client = Mistral(api_key=API_KEY)
# model = "mistral-medium-2505"
class MultiAgentBot:
    def __init__(self, llm: BaseLLMClient | None, web_search_engine: BaseWebSearchEngine | None):
        # self.application = Application.builder().token(token).build()
        self.application = get_application()
        self.llm = llm
        self.web_search_engine = web_search_engine
        # Инициализируем все обработчики
        self.handlers = [
            MessageHandlers(self),
            StartHandler(self),
            # CommandHandlers(self),
            # CallbackHandlers(self)
        ]
        self._setup_handlers()
    
    def _setup_handlers(self):
        for handler in self.handlers:
            handler.register_handlers(self.application)

    def process_user_message(self, update, context):
        user_id = str(update.effective_user.id)
        user_message = update.message.text
        prompt = get_prompt(user_message, self.web_search_engine)
        ans = self.llm.generate(messages=prompt)

        return ans


if __name__ == "__main__":
    # application = get_application()
    # start_handler = CommandHandler('start', start)

    # caps_handler = CommandHandler('caps', caps)
    # caps_handler = CommandHandler('code', code)
    # echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    
    # application.add_handler(start_handler)
    # application.add_handler(echo_handler)
    # application.add_handler(caps_handler) 
    #     
    # application.run_polling()
    pass