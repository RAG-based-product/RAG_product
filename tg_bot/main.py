import os
import sys
from dotenv import load_dotenv
from tg_bot_core import TelegramBot
import logging
# from models.mistral_llm_client import MistralLLMClient
# from web_search.tavily_web_search import TavilyWebSearchEngine

# from models.prompts import get_prompt # Закомментировано, так как не используется в main()
# Добавляем корневую директорию проекта в sys.path для корректного импорта
# Это гарантирует, что Python найдет модули типа tg_bot.bot_core
sys.path.append(os.path.dirname(os.path.abspath(__file__))) 

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def main():
    """
    Основная точка входа в приложение: 
    загружает переменные окружения, инициализирует LLM и инструменты, 
    и запускает Telegram Bot.
    """
    # Загрузка переменных окружения из .env файла
    load_dotenv() 

    # Проверка, что Telegram Bot Token загружен
    if not os.getenv("TELEGRAM_BOT_TOKEN"):
        error_msg = "ОШИБКА: TELEGRAM_BOT_TOKEN не загружен."
        logger.error(error_msg)
        sys.exit(1)
    
    # URL FastAPI (можно из переменной окружения)
    api_host = os.getenv("FASTAPI_HOST", "http://localhost")
    api_port = os.getenv("FASTAPI_PORT", "8000")
    api_url = f"{api_host}:{api_port}"
    
    try:
        logger.info("Инициализация Telegram Bot...")
        bot = TelegramBot(api_url=api_url)
        
        logger.info("Бот запускается и готов принимать команды...")
        bot.application.run_polling()
        
    except Exception as e:
        import traceback
        error_msg = f"Критическая ошибка: {e}\n{traceback.format_exc()}"
        logger.error(error_msg)
        sys.exit(1)

if __name__ == "__main__":
    main()