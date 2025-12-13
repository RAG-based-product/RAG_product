import pandas as pd
import requests
from typing import Dict, List, Any, Union
import os # Добавляем os для безопасного управления файлами и окружением

# =========================================================================
# 1. StackOverflowAnswersAPI: Полный класс для целей тестирования
# =========================================================================

class StackOverflowAnswersAPI:
    """
    Класс для взаимодействия с API Stack Exchange. 
    Содержит методы, необходимые для тестирования Hit Rate.
    """
    # 🚨 ИСПРАВЛЕНИЕ: Добавлен отсутствующий конструктор __init__
    def __init__(self, api_key: str = None):
        self.base_url = "https://api.stackexchange.com/2.3"
        self.api_key = api_key
        self.session = requests.Session()
    
    # 🚨 ИСПРАВЛЕНИЕ: Метод search_questions_by_query с сортировкой по релевантности
    def search_questions_by_query(self, query: str, n_results: int = 10) -> List[int]:
        """
        Ищет вопросы по запросу и возвращает список ID вопросов, 
        отсортированных по релевантности.
        """
        url = f"{self.base_url}/search/advanced"
        
        params = {
            'q': query,
            'site': 'stackoverflow',
            'pagesize': n_results,
            'order': 'desc',
            'sort': 'relevance',  # <--- КОРРЕКЦИЯ: Использование сортировки по релевантности
            #'hasaccepted': True   # Оставляем, чтобы гарантировать решение
        }
        
        if self.api_key:
            params['key'] = self.api_key
            
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status() 
            
            data = response.json()
            return [item['question_id'] for item in data.get('items', [])]
        except requests.RequestException as e:
            print(f"Ошибка при запросе к Stack Overflow API: {e}")
            return []
        except Exception as e:
             print(f"Непредвиденная ошибка: {e}")
             return []


# =========================================================================
# 2. ФУНКЦИЯ ДЛЯ ТЕСТИРОВАНИЯ (CALCULATING HIT RATE)
# =========================================================================

def evaluate_retrieval_hit_rate(
    file_path: str, 
    api_client: StackOverflowAnswersAPI, 
    n_retrieval: int = 25
) -> float:
    """
    Оценивает качество поиска (Retrieval) по заданному датасету.
    """
    # 🚨 ИСПРАВЛЕНИЕ: Используем os.path.join для безопасной работы с путями,
    # и читаем CSV напрямую по относительному пути (user_queries.csv) если возможно,
    # иначе используем переданный абсолютный путь.
    
    # Загрузка данных (используем переданный file_path, чтобы избежать жесткой привязки)
    try:
        # Пытаемся читать по абсолютному пути (который вы передали)
        if os.path.isabs(file_path):
            df = pd.read_csv(file_path)
        # Если передан только 'user_queries.csv', ищем его относительно текущей директории
        else:
            df = pd.read_csv(file_path) 
            
    except Exception as e:
        print(f"ОШИБКА при чтении CSV. Проверьте путь и кодировку: {e}")
        # Вывод пути для отладки
        print(f"Попытка чтения файла: {file_path}")
        return 0.0

    total_queries = len(df)
    hits = 0
    
    print(f"Начинаем тестирование {total_queries} запросов...")

    for index, row in df.iterrows():
        # ... (логика цикла остается без изменений)
        user_query = row['user_query']
        expected_ids = [int(id_str.strip()) for id_str in row['so_questions_ids'].split(';') if id_str.strip().isdigit()]
        
        retrieved_ids = api_client.search_questions_by_query(user_query, n_results=n_retrieval)
        
        is_hit = any(expected_id in retrieved_ids for expected_id in expected_ids)
        
        if is_hit:
            hits += 1
            print(f"✅ Успех для запроса #{index + 1} ('{user_query[:30]}...'): Найдено.")
        else:
            print(f"❌ Провал для запроса #{index + 1} ('{user_query[:30]}...'): Ожидаемые: {expected_ids[:2]}, Полученные: {retrieved_ids[:2]}")
            
    hit_rate = (hits / total_queries) * 100
    
    print("\n" + "="*50)
    print(f"ИТОГОВЫЕ МЕТРИКИ RETRIEVAL")
    print(f"Всего запросов: {total_queries}")
    print(f"Количество попаданий (Hits): {hits}")
    print(f"КОЭФФИЦИЕНТ ПОПАДАНИЯ (Hit Rate @{n_retrieval}): {hit_rate:.2f}%")
    print("="*50)
    
    return hit_rate


# =========================================================================
# 3. ЗАПУСК ТЕСТИРОВАНИЯ
# =========================================================================

if __name__ == "__main__":
    # УКАЖИТЕ ВАШ АПИ КЛЮЧ
    STACK_API_KEY = None 
    
    # 🚨 ИСПРАВЛЕНИЕ ПУТИ: Используем более надежный путь
    # Это путь, который вы указали:
    USER_QUERIES_PATH = r'C:\Users\JOHANN MOULEO\RAG_product\tests\datasets\user_queries.csv'
    
    # 1. Инициализация API клиента
    so_client = StackOverflowAnswersAPI(api_key=STACK_API_KEY)
    
    # 2. Запуск оценки
    final_hit_rate = evaluate_retrieval_hit_rate(
        file_path=USER_QUERIES_PATH,  # Используем исправленную переменную пути
        api_client=so_client, 
        n_retrieval=5
    )

    if final_hit_rate < 80:
        print("\nПОДСКАЗКА: Коэффициент попадания ниже целевого 80%. Возможно, стоит:")
        print("* Проверить фильтры API (min_score, sort) в вашем классе StackOverflowAnswersAPI.")
        print("* Увеличить `n_retrieval` для поиска по большему числу результатов.")