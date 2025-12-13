from rag.so_answers import StackOverflowAnswersAPI
from web_search.base_web_search_engine import BaseWebSearchEngine 
from typing import List, Dict, Any, Union

# Убедитесь, что StackOverflowAnswersAPI и BaseWebSearchEngine
# имеют правильные методы, как предполагается в этом коде.

def get_prompt(user_content: str, web_search_engine: BaseWebSearchEngine) -> List[Dict[str, str]]:
    """
    Формирует финальное сообщение (промпт) для LLM, обогащенное
    результатами поиска из интернета и Stack Overflow (RAG).
    
    Args:
        user_content: Исходный запрос пользователя.
        web_search_engine: Экземпляр поисковой системы для веб-поиска.
        
    Returns:
        Список сообщений (system/user) для передачи в LLM.
    """
    
    # 1. Поиск в интернете
    # Предполагается, что web_search_engine.search() возвращает 
    # список ID вопросов Stack Overflow или пустой список.
    try:
        web_results: List[Union[int, str]] = web_search_engine.search(user_content)
        # Если web_results возвращает ссылки или текст, а не ID, 
        # здесь потребуется дополнительная логика извлечения ID.
        print(f'Веб-поиск возвратил: {web_results}')
    except Exception as e:
        print(f"Ошибка при веб-поиске: {e}")
        web_results = []
    
    # 2. Получение данных Stack Overflow (SO)
    so_api = StackOverflowAnswersAPI()
    
    # Фильтруем web_results, оставляя только числовые ID (если web_results содержит смешанные типы)
    additional_question_ids = [int(q_id) for q_id in web_results if isinstance(q_id, int) or str(q_id).isdigit()]
    
    verified_answers = so_api.get_questions_with_answers(
        query=user_content,
        min_score=5,
        only_accepted=True,
        n_results=5,
        additional_question_ids=additional_question_ids
    )
    
    # 3. Форматирование контекста RAG
    rag_add = '\n\n--- КОНТЕКСТ STACK OVERFLOW ---\n'
    if not verified_answers:
        rag_add += 'Дополнительный контекст Stack Overflow не найден.\n'
    else:
        for qa in verified_answers:
            # Убеждаемся, что тела ответов не слишком длинные для промпта
            answer_body = qa['best_answer']['body'][:1500] + '...' # Обрезаем для безопасности
            
            rag_add += (
                f"\n[QID: {qa['question_id']}] "
                f"Вопрос: {qa['question_title']}\n"
                f"Рейтинг вопроса: {qa['question_score']}\n"
                f"Рейтинг ответа (Accepted: {qa['best_answer']['is_accepted']}): {qa['best_answer']['score']}\n"
                f"Тело вопроса: {qa['question_body'][:500]}...\n"
                f"Ответ: {answer_body}\n"
                f"Ссылка: {qa['url']}\n"
                f"---"
            )

    # 4. Формирование финального промпта для LLM
    message = [
        {
            "role": "system",
            "content": (
                "Ты — эксперт-программист, специализирующийся на объяснении сложных ошибок "
                "и предоставлении проверенных решений. Твоя задача — проанализировать "
                "запрос пользователя и предоставленный ниже контекст Stack Overflow, чтобы "
                "дать максимально точный, исчерпывающий и вежливый ответ.\n\n"
                "Инструкции:\n"
                "1. Объясни пользователю причину ошибки (если применимо) или дай четкое решение.\n"
                "2. Предложи конкретное решение, основанное на **самом рейтинговом** ответе из контекста.\n"
                "3. Приведи пример кода, используя информацию из контекста.\n"
                "4. Укажи ссылки на источники (если они есть в контексте).\n"
            ) + rag_add
        },
        {"role": "user", "content": user_content}
    ]

    return message

# Пример использования: Для тестирования вам понадобится фиктивный (Mock) BaseWebSearchEngine.
# class MockWebSearch(BaseWebSearchEngine):
#     def search(self, query):
#         # Имитация возврата ID вопросов SO из веб-поиска
#         if "nn.Module" in query:
#             return [13303681, 46166504]  # Пример реальных SO IDs
#         return []

# if __name__ == "__main__":
#     # Создаем фиктивный объект для имитации работы веб-поиска
#     mock_engine = MockWebSearch()
#     
#     # Протестируем
#     test_query = "What is difference between nn.Module and nn.Sequential in PyTorch?"
#     final_prompt = get_prompt(test_query, mock_engine)
#     
#     print("\n--- ФИНАЛЬНЫЙ СИСТЕМНЫЙ ПРОМПТ ДЛЯ LLM ---")
#     print(final_prompt[0]['content'])
#     print("\n--- ЗАПРОС ПОЛЬЗОВАТЕЛЯ ---")
#     print(final_prompt[1]['content'])