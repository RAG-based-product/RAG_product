import pandas as pd
import requests
from typing import List, Optional
import os
import logging
import time
from dotenv import load_dotenv

# =========================
# ЛОГИРОВАНИЕ
# =========================
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

# =========================
# STACK OVERFLOW API CLIENT
# =========================
class StackOverflowAnswersAPI:
    """
    Клиент для работы с Stack Exchange API
    """
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://api.stackexchange.com/2.3"
        self.api_key = api_key
        self.session = requests.Session()

    def search_questions_by_query(
        self,
        query: str,
        n_results: int = 100
    ) -> List[int]:
        """
        Ищет вопросы на Stack Overflow по текстовому запросу
        и возвращает список question_id
        """
        url = f"{self.base_url}/search/advanced"

        params = {
            "q": query,
            "site": "stackoverflow",
            "pagesize": n_results,
            "order": "desc",
            "sort": "votes",
        }

        if self.api_key:
            params["key"] = self.api_key

        try:
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()

            data = response.json()

            if "error_id" in data:
                logger.error(
                    f"StackExchange API error: {data.get('error_message')}"
                )
                return []

            return [
                item["question_id"]
                for item in data.get("items", [])
                if "question_id" in item
            ]

        except requests.RequestException as e:
            logger.error(f"HTTP/API error: {e}")
            return []


# =========================
# RETRIEVAL EVALUATION
# =========================
def evaluate_retrieval_metrics(
    file_path: str,
    api_client: StackOverflowAnswersAPI,
    k: int = 100,
    sleep_time: float = 0.5
) -> None:
    """
    Считает Hit Rate@K, Recall@K, Precision@K
    """

    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        logger.error(f"Ошибка чтения CSV: {e}")
        return

    total_queries = len(df)

    hits = 0
    recall_sum = 0.0
    precision_sum = 0.0

    logger.info("=" * 60)
    logger.info(f"Начинаем оценку retrieval для {total_queries} запросов")
    logger.info("=" * 60)

    for idx, row in df.iterrows():
        query = row["user_query"]

        expected_ids = []
        if pd.notna(row["so_questions_ids"]):
            expected_ids = [
                int(x.strip())
                for x in str(row["so_questions_ids"]).split(";")
                if x.strip().isdigit()
            ]

        time.sleep(sleep_time)

        retrieved_ids = api_client.search_questions_by_query(
            query, n_results=k
        )

        retrieved_set = set(retrieved_ids)
        expected_set = set(expected_ids)

        true_positives = len(retrieved_set & expected_set)

        hit = 1 if true_positives > 0 else 0
        recall = (
            true_positives / len(expected_set)
            if expected_set else 0.0
        )
        precision = (
            true_positives / len(retrieved_set)
            if retrieved_set else 0.0
        )

        hits += hit
        recall_sum += recall
        precision_sum += precision

        if hit:
            logger.info(
                f"[{idx+1}] HIT | Recall={recall:.2f} | Precision={precision:.4f} | {query[:40]}..."
            )
        else:
            logger.warning(
                f"[{idx+1}] MISS | Expected={list(expected_set)[:2]} | Retrieved={list(retrieved_set)[:2]}"
            )

    hit_rate = hits / total_queries * 100
    mean_recall = recall_sum / total_queries * 100
    mean_precision = precision_sum / total_queries * 100

    logger.info("\n" + "=" * 60)
    logger.info("ИТОГОВЫЕ МЕТРИКИ RETRIEVAL")
    logger.info(f"Hit Rate @{k}: {hit_rate:.2f}%")
    logger.info(f"Mean Recall @{k}: {mean_recall:.2f}%")
    logger.info(f"Mean Precision @{k}: {mean_precision:.4f}%")
    logger.info("=" * 60)


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    load_dotenv()

    STACK_API_KEY = os.getenv("STACK_API_KEY")

    if STACK_API_KEY:
        logger.info("STACK_API_KEY загружен.")
    else:
        logger.warning("STACK_API_KEY не найден (возможен rate limit).")

    DATASET_PATH = r"C:\Users\JOHANN MOULEO\RAG_product\backend\tests\datasets\eng_dataset.csv"

    if not os.path.exists(DATASET_PATH):
        logger.error(f"Датасет не найден: {DATASET_PATH}")
    else:
        so_client = StackOverflowAnswersAPI(api_key=STACK_API_KEY)

        evaluate_retrieval_metrics(
            file_path=DATASET_PATH,
            api_client=so_client,
            k=100,
            sleep_time=0.5
        )
