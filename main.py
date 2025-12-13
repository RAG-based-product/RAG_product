import os
import sys
from dotenv import load_dotenv

# Добавляем корневую директорию проекта в sys.path для корректного импорта
# Это гарантирует, что Python найдет модули типа tg_bot.bot_core
sys.path.append(os.path.dirname(os.path.abspath(__file__))) 

# Импорты ваших компонентов
from tg_bot.bot_core import MultiAgentBot
from models.mistral_llm_client import MistralLLMClient
from web_search.tavily_web_search import TavilyWebSearchEngine
# from models.prompts import get_prompt # Закомментировано, так как не используется в main()

# =========================================================================
# 1. ОСНОВНАЯ ФУНКЦИЯ ПРИЛОЖЕНИЯ
# =========================================================================

def main():
    """
    Основная точка входа в приложение: 
    загружает переменные окружения, инициализирует LLM и инструменты, 
    и запускает Telegram Bot.
    """
    
    # 🚨 КРИТИЧЕСКИ ВАЖНО: Загрузить переменные окружения из .env 
    # (Это решает все ошибки типа ValueError: ... not found)
    load_dotenv() 

    # Проверка, что LLM API ключ загружен
    if not os.getenv("MISTRAL_API_KEY"):
        print("ОШИБКА: MISTRAL_API_KEY не загружен. Проверьте ваш файл .env.")
        return

    # Проверка, что Telegram Bot Token загружен
    if not os.getenv("TELEGRAM_BOT_TOKEN"):
        print("ОШИБКА: TELEGRAM_BOT_TOKEN не загружен. Проверьте ваш файл .env.")
        return
    
    try:
        # 1. Инициализация LLM
        print("Инициализация Mistral LLM Client...")
        llm = MistralLLMClient()
        
        # 2. Инициализация Web Search Engine
        print("Инициализация Tavily Web Search Engine...")
        web_search_engine = TavilyWebSearchEngine()
        
        # 3. Создание и запуск бота
        print("Инициализация MultiAgentBot...")
        # MultiAgentBot инициализирует Telegram Bot Application и добавляет обработчики
        bot = MultiAgentBot(llm, web_search_engine)
        
        print("✅ Мультиагентный бот успешно инициализирован.")
        print("🌐 Бот запускается и готов принимать команды...")
        
        # Бот блокирует выполнение и ждет входящих сообщений
        bot.application.run_polling() 

    except Exception as e:
        print(f"Критическая ошибка при запуске main(): {e}")
        # Выводит более подробную информацию об ошибке
        # import traceback
        # traceback.print_exc()

# =========================================================================
# 2. ЗАПУСК
# =========================================================================

if __name__ == "__main__":
    main()