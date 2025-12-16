from web_search.base_web_search_engine import BaseWebSearchEngine
from tavily import TavilyClient
import os
from dotenv import load_dotenv

class TavilyWebSearchEngine(BaseWebSearchEngine):
    """
    TavilyWebSearchEngine — реализация поиска в интернете через Tavily API.
    """

    def __init__(self):
        load_dotenv()
        TAVILY_API_TOKEN = os.environ.get("TAVILY_API_TOKEN")
        if not TAVILY_API_TOKEN:
            raise ValueError("TAVILY_API_TOKEN not found!")
        else:
            print("TAVILY_API_TOKEN loaded successfully!")
            self.tavily_client = TavilyClient(api_key=TAVILY_API_TOKEN)

    def search(self, query, top_k=5, include_domains=["stackoverflow.com/questions"]):
        """
        Выполнить поиск через Tavily API.
        Возвращает список словарей с 'title', 'url' и 'content'.
        """
        response = self.tavily_client.search(
            query=query,
            max_results=top_k,
            include_domains=include_domains,
            include_answer=False, 
            include_images=False,
        )
        return self.parse_results(response) 
    
    def parse_results(self, raw_results):
        """
        Преобразовать "сырые" результаты Tavily API в список документов RAG.
        """
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
