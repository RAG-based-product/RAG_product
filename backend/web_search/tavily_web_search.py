from web_search.base_web_search_engine import BaseWebSearchEngine
from tavily import TavilyClient
import re
from typing import Optional, Set
import os
from dotenv import load_dotenv
import logging
import sys
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class TavilyWebSearchEngine(BaseWebSearchEngine):
    """
    TavilyWebSearchEngine — реализация поиска в интернете через Tavily API.
    """

    def __init__(self):
        load_dotenv()
        TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
        if not TAVILY_API_KEY:
            logger.error("TAVILY_API_KEY не найден!")
            raise ValueError("TAVILY_API_KEY не найден!")
        else:
            logger.info("TAVILY_API_KEY успешно загружен!")
            self.tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

    def search(self, query, top_k=5, include_domains=["stackoverflow.com/questions"]):
        """
        Выполнить поиск через Tavily API.
        Возвращает список словарей с 'title', 'url' и 'content'.
        """
        try:
            response = self.tavily_client.search(
                query=query,
                max_results=top_k,
                include_domains=include_domains,
                include_answer=False, 
                include_images=False,
            )
            return self.parse_results(response) 
        except Exception as e:
            logger.error(f"Ошибка при поиске через Tavily API: {str(e)}")
            return []
    
    def parse_results(self, raw_results):
        """
        Преобразовать "сырые" результаты Tavily API в список документов RAG.
        """
        try:
            documents = []
            # Tavily возвращает результаты в поле "results"
            items = raw_results.get("results", [])
            
            # Сохраняем только необходимые поля для RAG и вывода источников
            for item in items:
                documents.append({
                    'title': item.get('title', 'Нет заголовка'),
                    'url': item.get('url', '#'),
                    # Поле 'content' содержит краткое описание страницы
                    'content': item.get('content', 'Содержимое не доступно.') 
                })
            return documents
        except Exception as e:
            logger.error(f"Ошибка при парсинге результатов через Tavily API: {str(e)}")
            return raw_results

    def _extract_question_id_from_url(self, url: str) -> Optional[int]:
        """
        Извлекает ID вопроса из URL StackOverflow.
        Пример: https://stackoverflow.com/questions/12345/... -> 12345
        """
        try:
            match = re.search(r'/questions/(\d+)/', url)
            if match:
                return int(match.group(1))
        except Exception as e:
            logger.warning(f"Ошибка при извлечении ID из URL {url}: {e}")
        return None

    def get_ids(self, web_search_results):
        # Извлекаем ID вопросов из URL
        web_search_question_ids: Set[int] = set()

        for result in web_search_results:
            question_id = self._extract_question_id_from_url(result.get('url', ''))
            if question_id:
                web_search_question_ids.add(question_id)

        return web_search_question_ids