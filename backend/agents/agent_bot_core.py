# backend/agents/agent_bot_core.py
from typing import List, Tuple, Dict, Any, Set, Optional
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
import logging
import json
import os
from agents.base_agent import BaseAgent
from models.base_llm_client import BaseLLMClient
from web_search.base_web_search_engine import BaseWebSearchEngine
from models.prompts import Source, get_prompt, need_web_search_prompt, NeedWebSearchResponse
from rag.so_answers import StackOverflowAnswersAPI
from rag.redis_cache import RedisCache
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class AgentBot(BaseAgent):
    """
    Сервис для обработки RAG-запросов.
    Инкапсулирует логику Retrieval-Augmented Generation.
    """
    
    def __init__(
        self, 
        name: str, 
        llm_client: BaseLLMClient, 
        system_prompt: str,
        web_search_engine: BaseWebSearchEngine = None
    ):
        super().__init__(name=name, llm_client=llm_client, system_prompt=system_prompt)
        self.web_search_engine = web_search_engine
        
        # Инициализация StackOverflow API 
        try:
            api_key=os.getenv("STACKOVERFLOW_API_KEY")
        except:
            api_key = None #до 1000 запросов ключ не требуется
        self.so_api = StackOverflowAnswersAPI(api_key)
        
        # Инициализация кэша для веб-поиска
        self.web_search_cache = RedisCache(
            host=os.getenv("REDIS_HOST", "redis"),
            prefix="web_search",
            ttl=6 * 3600  # 6 часов
        )
    


    async def process(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Обрабатывает запрос пользователя через RAG-пайплайн.
        
        Args:
            message: Сообщение пользователя
            context: Дополнительный контекст (опционально)
        
        Returns:
            Dict[str, Any]: {
                "answer": str - ответ LLM,
                "sources": List[Source] - список источников
            }
        """
        if context is None:
            context = {}
        
        user_query = message
        so_question_ids: Set[int] = set()
        final_so_results = []
        sources_list: List[Source] = []
        # 0. Проверка запроса на необходимость поиска в интернете
        need_web_search = False
        need_web_search_prompt_text = need_web_search_prompt(user_query)
        
        # Преобразуем строку промпта в формат messages для LLM
        messages = [{"role": "user", "content": need_web_search_prompt_text}]
        
        first_answer = await self.llm_client.generate(messages, 
                    expected_output_parser=JsonOutputParser(pydantic_object=NeedWebSearchResponse)
                    )
        logger.info(f"Первый ответ LLM: {first_answer}")
        
        # first_answer уже является словарем (распарсенным JSON)
        need_web_search = first_answer.get('need_web_search', True)
        web_search_comment = first_answer.get('comment', user_query)

        if not need_web_search:
            logger.info(f"Не нужно искать информацию в интернете. Комментарий: {web_search_comment}")
            return {
                "answer": web_search_comment,
                "sources": []
            }
        else:
            logger.info(f"Нужно искать информацию в интернете. Комментарий: {web_search_comment}")
        # 1. Проверка кэша веб-поиска
        logger.info("Шаг 1: Проверка кэша веб-поиска...")
        web_search_results = None
        try:
            cached_web_search = self.web_search_cache.get(web_search_comment)
            if cached_web_search:
                # logger.info("Кэш веб-поиска найден (HIT)")
                web_search_results = cached_web_search.get("results", [])
                web_search_question_ids = set(cached_web_search.get("question_ids", []))
                logger.info(f"Кэш веб-поиска найден. Найдено ID вопросов: {web_search_question_ids}")
        except Exception as e:
            logger.error(f"Ошибка при проверке кэша веб-поиска: {e}")
        
        # 2. Веб-поиск похожих запросов на StackOverflow, получение IDS запросов, и загрузка результатов в кэш
        if web_search_results is None:
            logger.info("Шаг 2: Выполнение веб-поиска через Tavily...")
            try:
                if not self.web_search_engine:
                    logger.warning("WebSearchEngine не инициализирован, пропускаем веб-поиск")
                else:
                    web_search_results = self.web_search_engine.search(user_query, top_k=5)
                    
                    web_search_question_ids = self.web_search_engine.get_ids(web_search_results)
                    
                    logger.info(f"Веб-поиск завершен. Найдено ID вопросов: {web_search_question_ids}")
                    # Сохраняем в кэш
                    try:
                        self.web_search_cache.set(web_search_comment, {
                            "results": web_search_results,
                            "question_ids": list(web_search_question_ids)
                        })
                        logger.info(f"Результаты поиска сохранены в кэш веб-поиска.")
                    except Exception as e:
                        logger.error(f"Ошибка при сохранении в кэш веб-поиска: {e}")
            except Exception as e:
                logger.error(f"Ошибка при веб-поиске через Tavily: {e}")
                web_search_results = []
                web_search_question_ids = set()
        
        # 3. Поиск StackOverflow похожих запросов
        logger.info("Шаг 3: Поиск похожих вопросов на StackOverflow через API...")
        try:
            so_search_results = self.so_api.get_questions_with_answers(
                query=user_query,
                min_score=1,
                only_accepted=True,
                has_accepted_answer=True,
                n_results=10
            )
            logger.info(f"StackOverflow API поиск завершен. Найдено {len(so_search_results)} вопросов.")
            so_question_ids = {q['question_id'] for q in so_search_results}
            if len(so_question_ids) > 0:
                logger.info(f"StackOverflow API поиск завершен. Найдено ID вопросов: {so_question_ids}")

        except Exception as e:
            logger.error(f"Ошибка при поиске на StackOverflow: {e}")
            so_search_results = []
            so_question_ids = set()
        
        # 4. Объединение IDS запросов из п. 2 и 3
        logger.info("Шаг 4: Объединение ID вопросов...")
        all_question_ids = list(web_search_question_ids | so_question_ids)
        logger.info(f"Всего уникальных ID вопросов: {len(all_question_ids)}")
        
        # 5. Получение аппрувленных и оцененных ответов на StackOverflow по каждому из IDS
        logger.info("Шаг 5: Получение полных данных по вопросам с ответами...")
        try:
            # Используем метод get_questions_with_answers с additional_question_ids
            # для получения данных по всем вопросам, включая те, что были найдены через веб-поиск
            final_so_results = self.so_api.get_questions_with_answers(
                query=user_query,
                min_score=1,
                only_accepted=True,
                has_accepted_answer=True,
                n_results=10,
                additional_question_ids=all_question_ids if all_question_ids else None
            )
            
            # Формируем источники из результатов StackOverflow
            for qa in final_so_results:
                try:
                    source = Source(
                        title=qa.get('question_title', 'Без заголовка'),
                        url=qa.get('url', '#'),
                        content=f"Вопрос: {qa.get('question_body', '')}\n\nОтвет: {qa.get('best_answer', {}).get('body', '')}"
                    )
                    sources_list.append(source)
                except Exception as e:
                    logger.warning(f"Ошибка при формировании источника: {e}")
                    continue
        except Exception as e:
            logger.error(f"Ошибка при получении полных данных по вопросам: {e}")
        
        # 6. Формирование промпта с учетом полученных данных
        logger.info("Шаг 6: Формирование промпта...")
        final_prompt = get_prompt(user_query, sources_list)

        # 7. Передача промпта в llm_client для получения ответа для пользователя
        logger.info("Шаг 7: Генерация ответа через LLM...")
        try:
            answer_text = await self._call_llm(final_prompt)
        except Exception as e:
            logger.error(f"Ошибка при генерации LLM: {e}")
            answer_text = "Модель LLM не смогла сгенерировать ответ."
        
        logger.info("Пайплайн успешно завершен")
        return {
            "answer": answer_text,
            "sources": sources_list
        }