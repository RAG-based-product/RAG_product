from web_search.base_web_search_engine import BaseWebSearchEngine
from tavily import TavilyClient
import asyncio
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
            raise ValueError("❌ TAVILY_API_TOKEN not found!")
        else:
            print("✅ TAVILY_API_TOKEN loaded successfully!")
            self.tavily_client = TavilyClient(api_key=TAVILY_API_TOKEN)

    def search(self, query, top_k=5, include_domains=["stackoverflow.com/questions"]):
        """
        Выполнить поиск через Tavily API.
        """
        # Официальный клиент синхронный, поэтому оборачиваем в asyncio.to_thread
        # response = await asyncio.to_thread(
        #     self.tavily_client.search,
        #     query=query,
        #     max_results=top_k
        # )
        # print(f"Searching for query: {query}")
        response = self.tavily_client.search(
            query=query,
            max_results=top_k,
            include_domains=include_domains
            )
        # print(f"Response: {response}")
        return self.parse_results(response)
    
    def parse_questions_ids_from_results(self, raw_results):
        """
        Преобразовать "сырые" результаты Tavily API в список документов.
        """
        questions_ids = []
        # Tavily возвращает результаты в поле "results"
        items = raw_results.get("results", [])
        for item in items:
            url = item.get("url") # https://stackoverflow.com/questions/71374232/center-argument-must-be-a-pair-of-numbers
            questions_ids.append(url.split("/")[4]) # 71374232

        print('TavilyWebSearchEngine returns questions_ids ', questions_ids)
        return questions_ids

    def parse_results(self, raw_results):
        return self.parse_questions_ids_from_results(raw_results)

if __name__ == "__main__":

    engine = TavilyWebSearchEngine()
    query = "pygame.draw.circle center argument must be a pair of numbers"
    include_domains = ["stackoverflow.com/questions"]
    # results = asyncio.run(engine.search(query))
    results = engine.search(query, include_domains=include_domains)
    print(f"Search results for query: {query}")
    print(results)
