import pandas as pd
import requests
from typing import List, Optional
import os 
import logging
import time
from dotenv import load_dotenv 

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# =========================================================================
# 1. StackOverflowAnswersAPI: Полный класс для целей тестирования
# =========================================================================

class StackOverflowAnswersAPI:
    """
    Класс для взаимодействия с API Stack Exchange. 
    Содержит методы, необходимые для тестирования Hit Rate.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://api.stackexchange.com/2.3"
        self.api_key = api_key
        self.session = requests.Session()
    
    def search_questions_by_query(self, query: str, n_results: int = 10) -> List[int]:
        """
        Ищет вопросы по запросу и возвращает список ID вопросов.
        """
        url = f"{self.base_url}/search/advanced"
        
        params = {
            'q': query,
            'site': 'stackoverflow',
            'pagesize': n_results,
            'order': 'desc',
            'sort': 'votes', 
            'filter': 'default' 
        }
        
        if self.api_key:
            params['key'] = self.api_key
            
        try:
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status() 
    
            data = response.json()

            if 'error_id' in data:
                logger.error(f"API Stack Exchange вернул ошибку в теле ответа: {data.get('error_message')}")
                return []
            
            question_ids = [item.get('question_id') for item in data.get('items', []) if item.get('question_id') is not None]
            
            if not question_ids:
                logger.warning(f"0 ID вопросов получено. Запрос: '{query[:40]}...'")

            return question_ids
            
        except requests.HTTPError as e:
            logger.error(f"HTTP ОШИБКА ({response.status_code}) при запросе к SO API: {e}")
            return []
        except requests.RequestException as e:
            logger.error(f"Ошибка при запросе к Stack Overflow API: {e}")
            return []
        except Exception as e:
            logger.error(f"Непредвиденная ошибка при обработке JSON: {e}")
            return []

# =========================================================================
# 2. ФУНКЦИЯ ДЛЯ ТЕСТИРОВАНИЯ (CALCULATING HIT RATE)
# =========================================================================

def evaluate_retrieval_hit_rate(
    file_path: str, 
    api_client: StackOverflowAnswersAPI, 
    n_retrieval: int = 100
) -> float:
    """
    Оценивает качество поиска (Retrieval) по заданному датасету.
    """
    
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        logger.error(f"ОШИБКА при чтении CSV. Проверьте путь и кодировку: {e}")
        logger.error(f"Попытка чтения файла: {file_path}")
        return 0.0

    total_queries = len(df)
    hits = 0
    
    logger.info("\n" + "="*50)
    logger.info(f"Начинаем тестирование {total_queries} запросов...")
    logger.info("="*50)

    for index, row in df.iterrows():
        user_query = row['user_query']
        expected_ids = []
        try:
            if pd.notna(row['so_questions_ids']):
                expected_ids = [int(id_str.strip()) for id_str in str(row['so_questions_ids']).split(';') if id_str.strip().isdigit()]
        except Exception:
            continue
            
        time.sleep(0.5) 

        retrieved_ids = api_client.search_questions_by_query(user_query, n_results=n_retrieval)
        
        is_hit = any(expected_id in retrieved_ids for expected_id in expected_ids)
        
        if is_hit:
            hits += 1
            logger.info(f"Успех для запроса #{index + 1} ('{user_query[:30]}...'): Найдено.")
        else:
            logger.warning(f"Провал для запроса #{index + 1} ('{user_query[:30]}...'): Ожидаемые: {expected_ids[:2]}, Полученные: {retrieved_ids[:2]}")
            
    hit_rate = (hits / total_queries) * 100
            
    logger.info("\n" + "="*50)
    logger.info(f"ИТОГОВЫЕ МЕТРИКИ RETRIEVAL")
    logger.info(f"Всего запросов: {total_queries}")
    logger.info(f"Количество попаданий (Hits): {hits}")
    logger.info(f"КОЭФФИЦИЕНТ ПОПАДАНИЯ (Hit Rate @{n_retrieval}): {hit_rate:.2f}%")
    logger.info("="*50)
    
    return hit_rate


# =========================================================================
# 3. ЗАПУСК ТЕСТИРОВАНИЯ
# =========================================================================

if __name__ == "__main__":
    load_dotenv()
    STACK_API_KEY = os.environ.get("STACK_API_KEY") 
    
    if STACK_API_KEY:
        logger.info("STACK_API_KEY успешно загружен.")
    else:
        logger.warning("STACK_API_KEY не найден. Возможен Rate Limit API Stack Exchange.")

    # Путь к вашему датасету
    USER_QUERIES_PATH = r'C:\Users\JOHANN MOULEO\RAG_product\tests\datasets\eng_dataset.csv'
    
    if not os.path.exists(USER_QUERIES_PATH):
        logger.error(f"Файл датасета не найден по указанному пути: {USER_QUERIES_PATH}")
    else:
        # 1. Инициализация API клиента
        so_client = StackOverflowAnswersAPI(api_key=STACK_API_KEY)
        
        # 2. Запуск оценки
        final_hit_rate = evaluate_retrieval_hit_rate(
            file_path=USER_QUERIES_PATH, 
            api_client=so_client, 
            n_retrieval=100
        )