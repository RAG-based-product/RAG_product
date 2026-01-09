from typing import List, Tuple
from pydantic import BaseModel
import logging
from web_search.base_web_search_engine import BaseWebSearchEngine

logger = logging.getLogger(__name__)

# --- Модели данных ---

class Source(BaseModel):
    """Представляет внешний источник информации."""
    title: str
    url: str
    content: str # Содержимое, используемое для промпта LLM

class NeedWebSearchResponse(BaseModel):
    need_web_search: bool
    comment: str

def need_web_search_prompt(user_query: str) -> str:
    """
    Формирует промпт для проверки необходимости поиска в интернете.
    """
    prompt = f"""
    Вы — экспертный ассистент RAG. 
    Определите, содержит ли текст пользователя технический вопрос, на который нужно ответить.
    Если нужно, то переведите запрос пользователя на английский язык и в поле комментария укажите ключевые слова для поиска на английском языке.
    Если не нужно, то в поле комментария приведите вежливый ответ пользователю на русском языке.
    Верните только JSON со следующими полями:
    - need_web_search: bool - нужно ли искать информацию в интернете
    - comment: str - только ключевые слова для поиска на английском языке, или вежливый ответ пользователю.
    ВАЖНО: Верните ТОЛЬКО валидный JSON без markdown разметки, без обратных кавычек, без дополнительного текста.
    Примеры:
    user_query_example_1: 'I have a function template f, defining in its body a local class A with another nested class B. 
    Both classes are not templates. 
    Must I name the inner class as typename A::B or shorter variant A::B is ok as well?'
    answer_example_1:
        "need_web_search": true
        "comment": 'local nested classes in function templates need typename for naming'
    user_query_example_2: 'Привет, что ты умеешь?'
    answer_example_2:
        "need_web_search": false
        "comment": "Привет! Я могу помочь вам с вашими техническими вопросами найти решение с помощью моих знаний и информации из StackOverflow. Что вы хотите узнать?"
    user_query: '{user_query}'
    answer_json:
    """
    return prompt

def get_prompt(user_query: str, sources_list: List[Source]) -> str:
    """
    Выполняет поиск в Интернете, форматирует результаты в контекст 
    и возвращает финальный промпт для LLM вместе со списком источников.
    """
    
    # Извлечение: Получаем результаты поиска
    
    context_text = f"Документы, найденные в процессе поиска:\n"
    for i, source in enumerate(sources_list):
        context_text += f"{i+1}. {source.title}\n{source.content}\n\n"
    
    # Создание финального промпта
    final_prompt = f"""
    Вы — экспертный ассистент RAG. Используйте СТРОГО только информацию, 
    представленную в секции "КОНТЕКСТ", для ответа на вопрос пользователя на русском языке. 
    Ваш ответ должен быть точным и лаконичным.
    В конце ответа укажите краткое описание по каждому источнику из контекста.
    ---
    КОНТЕКСТ:
    {context_text}
    ---
    
    ВОПРОС ПОЛЬЗОВАТЕЛЯ: {user_query}
    ---
    
    ОТВЕТ:
    """
    
    return final_prompt