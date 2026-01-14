from telegram.ext import Application
from handlers.message_handlers import MessageHandler as BotMessageHandler
from handlers.start_handler import start_handler
from utils import get_application
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

class TelegramBot:
    """
    Главный класс Telegram бота.
    Отвечает только за инициализацию и регистрацию обработчиков.
    """
    
    def __init__(self, api_url: str):
        """
        Args:
            api_url: URL FastAPI сервиса
        """
        self.application: Application = get_application()
        
        # Инициализация обработчиков с передачей только необходимых данных
        self.handlers = [
            BotMessageHandler(api_url),  # Передаем только URL, а не весь объект
            start_handler,
        ]
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Регистрирует обработчики в приложении Telegram."""
        for handler in self.handlers:
            if hasattr(handler, 'register_handlers'):
                handler.register_handlers(self.application)
            else:
                self.application.add_handler(handler)