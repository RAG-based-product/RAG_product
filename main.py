from tg_bot.bot_core import MultiAgentBot
# from utils.config import Config
# from core.dependencies import setup_dependencies
from models.mistral_llm_client import MistralLLMClient
from models.prompts import get_prompt
from web_search.tavily_web_search import TavilyWebSearchEngine
def main():
    # Загружаем конфигурацию
    # config = Config()
    
    # Настраиваем зависимости (Dependency Injection)
    # setup_dependencies(config)
    llm = MistralLLMClient()
    # Инициализируем поисковик
    web_search_engine = TavilyWebSearchEngine()

    # Создаем и запускаем бота
    bot = MultiAgentBot(llm, web_search_engine)
    
    print("Мультиагентный бот запускается...")
    bot.application.run_polling()

if __name__ == "__main__":
    # pr = get_prompt("What is difference between nn.Module and nn.Sequential")

    # print(pr)
    # pass
    main()