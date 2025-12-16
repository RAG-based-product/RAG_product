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

def get_prompt(user_query: str, web_search_engine: BaseWebSearchEngine) -> Tuple[str, List[Source]]:
    """
    Выполняет поиск в Интернете, форматирует результаты в контекст 
    и возвращает финальный промпт для LLM вместе со списком источников.
    """
    
    # Извлечение: Получаем результаты поиска
    try:
        search_results_raw = web_search_engine.search(user_query)
        
    except Exception as e:
        logger.error(f"Ошибка при веб-поиске (Tavily): {e}")
        # Возвращаем промпт с ошибкой и пустые источники
        error_prompt = f"""
        Вы — помощник RAG. При поиске информации произошла ошибка. 
        Пожалуйста, сообщите пользователю, что поиск не удался.
        ОШИБКА: {e}
        ВОПРОС ПОЛЬЗОВАТЕЛЯ: {user_query}
        """
        return error_prompt, []


    context_text = ""
    sources_list: List[Source] = []
    
    # Обработка и форматирование результатов (Предполагается, что search() вернул список словарей)
    for i, result in enumerate(search_results_raw):
        # Преобразование словаря в модель Source
        source = Source(
            title=result.get('title', 'Без заголовка'),
            url=result.get('url', '#'),
            content=result.get('content', 'Содержимое недоступно')
        )
        
        # Добавляем содержимое в контекст для LLM
        context_text += f"Документ {i+1}:\nЗаголовок: {source.title}\nСодержимое: {source.content}\n\n"
        
        # Сохраняем источник для вывода пользователю
        sources_list.append(source)

    # Создание финального промпта
    final_prompt = f"""
    Вы — экспертный ассистент RAG. Используйте СТРОГО только информацию, 
    представленную в секции "КОНТЕКСТ", для ответа на вопрос пользователя на русском языке. 
    Ваш ответ должен быть точным и лаконичным.

    ---
    КОНТЕКСТ:
    {context_text}
    ---
    
    ВОПРОС ПОЛЬЗОВАТЕЛЯ: {user_query}
    ---
    
    ОТВЕТ:
    """
    
    return final_prompt, sources_list