import asyncio
from tg_bot.bot_core import MultiAgentBot
# from utils.config import Config
# from core.dependencies import setup_dependencies
from models.mistral_llm_client import MistralLLMClient
from models.prompts import get_prompt

def main():
    # Загружаем конфигурацию
    # config = Config()
    
    # Настраиваем зависимости (Dependency Injection)
    # setup_dependencies(config)
    llm = MistralLLMClient()
    
    # Создаем и запускаем бота
    bot = MultiAgentBot(llm)
    
    print("Мультиагентный бот запускается...")
    bot.application.run_polling()

if __name__ == "__main__":
    # pr = get_prompt("What is difference between nn.Module and nn.Sequential")

    # print(pr)
    # pass
    main()