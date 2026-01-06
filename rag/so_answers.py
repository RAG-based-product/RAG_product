from typing import Dict, List, Any, Optional
import requests
import re
from html import unescape
from rag.redis_cache import RedisCache


class StackOverflowAnswersAPI:
    def __init__(self, api_key: str = None):
        self.base_url = "https://api.stackexchange.com/2.3"
        self.api_key = api_key
        self.session = requests.Session()
        
        self.cache = RedisCache(
            host="redis",  # "localhost" hors docker
            prefix="so_answers",
            ttl=6 * 3600  
        )

    # ----------------------------------------------------------------------
    def get_questions_with_answers(
        self,
        query: str,
        tags: Optional[List[str]] = None,
        min_score: int = 0,
        only_accepted: bool = True,
        has_accepted_answer: bool = True,
        n_results: int = 10,
        additional_question_ids: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        
        
        cache_payload = {
            "query": query,
            "tags": tags,
            "min_score": min_score,
            "only_accepted": only_accepted,
            "has_accepted_answer": has_accepted_answer,
            "n_results": n_results,
            "additional_question_ids": additional_question_ids
        }

        cached = self.cache.get(cache_payload)
        if cached:
            print("Redis cache HIT (StackOverflow)")
            return cached

        url = f"{self.base_url}/search/advanced"

        params = {
            'q': query,
            'site': 'stackoverflow',
            'pagesize': n_results,
            'order': 'desc',
            'sort': 'votes',
            'filter': 'withbody',
            'hasaccepted': has_accepted_answer
        }

        if tags:
            params['tagged'] = ';'.join(tags)

        if self.api_key:
            params['key'] = self.api_key

        response = self.session.get(url, params=params)

        if response.status_code != 200:
            print(f"Ошибка API: {response.status_code}")
            return []

        try:
            data = response.json()
            questions = data.get('items', [])
        except Exception as e:
            print(f"Ошибка JSON: {e}")
            return []

        # фильтрация по рейтингу
        filtered_questions = [
            q for q in questions if q.get('score', 0) >= min_score
        ]

        print("SO Answers API returns q_ids:", [q['question_id'] for q in filtered_questions])

        # При необходимости — загрузка дополнительных вопросов по ID
        if additional_question_ids:
            extra_questions = self._get_questions_by_ids(additional_question_ids)

            # Исключаем дубликаты
            seen_ids = {q['question_id'] for q in filtered_questions}
            extra_questions = [q for q in extra_questions if q['question_id'] not in seen_ids]

            filtered_questions.extend(extra_questions)

        # return self._enrich_with_best_answers(filtered_questions, only_accepted)
    
        result = self._enrich_with_best_answers(filtered_questions, only_accepted)
        self.cache.set(cache_payload, result)
        return result

    # ----------------------------------------------------------------------
    def _get_questions_by_ids(self, additional_question_ids: List[int]) -> List[Dict[str, Any]]:
        """Получение вопросов по ID"""
        questions = []

        for qid in additional_question_ids:
            url = f"{self.base_url}/questions/{qid}"

            params = {
                'order': 'desc',
                'sort': 'activity',
                'site': 'stackoverflow',
                'filter': '!nNPvSNPI7A'
            }

            r = self.session.get(url, params=params)

            if r.status_code != 200:
                print(f"Ошибка API для вопроса {qid}: {r.status_code}")
                continue

            try:
                data = r.json()
                question = data.get('items', [])[0]
                questions.append(question)
            except Exception as e:
                print(f"Ошибка при парсинге вопроса {qid}: {e}")

        return questions

    # ----------------------------------------------------------------------
    def _enrich_with_best_answers(
        self,
        questions: List[Dict],
        only_accepted: bool
    ) -> List[Dict]:

        enriched = []

        for question in questions:
            answers = self._get_question_answers(question['question_id'])
            if not answers:
                continue

            best_answer = self._select_best_answer(answers, only_accepted)
            if not best_answer:
                continue

            enriched.append({
                'question_id': question['question_id'],
                'question_title': question.get('title', ''),
                'question_body': self._clean_html(question.get('body', '')),
                'question_score': question.get('score', 0),
                'question_tags': question.get('tags', []),
                'question_views': question.get('view_count', 0),
                'answer_count': question.get('answer_count', 0),
                'url': question.get('link'),
                'accepted_answer_id': question.get('accepted_answer_id'),
                'best_answer': {
                    'answer_id': best_answer['answer_id'],
                    'body': self._clean_html(best_answer.get('body', '')),
                    'score': best_answer.get('score', 0),
                    'is_accepted': best_answer.get('is_accepted', False),
                    'owner_reputation': best_answer.get('owner', {}).get('reputation', 0)
                }
            })

        return enriched

    # ----------------------------------------------------------------------
    def _get_question_answers(self, question_id: int) -> List[Dict]:
        url = f"{self.base_url}/questions/{question_id}/answers"

        params = {
            'site': 'stackoverflow',
            'order': 'desc',
            'sort': 'votes',
            'filter': 'withbody',
            'pagesize': 20
        }

        if self.api_key:
            params['key'] = self.api_key

        r = self.session.get(url, params=params)
        if r.status_code != 200:
            return []

        return r.json().get('items', [])

    # ----------------------------------------------------------------------
    def _select_best_answer(self, answers: List[Dict], only_accepted: bool):
        if only_accepted:
            accepted = [a for a in answers if a.get('is_accepted')]
            return accepted[0] if accepted else None

        # иначе — лучший по score + репутации автора
        return sorted(
            answers,
            key=lambda x: (
                x.get('score', 0),
                x.get('owner', {}).get('reputation', 0)
            ),
            reverse=True
        )[0]

    # ----------------------------------------------------------------------
    def _clean_html(self, html_text: str) -> str:
        clean = re.compile('<.*?>')
        text = re.sub(clean, '', html_text)
        text = unescape(text)
        return ' '.join(text.split())


# ----------------------------------------------------------------------
def test_get_questions_with_answers():
    api = StackOverflowAnswersAPI()

    results = api.get_questions_with_answers(
        query="center argument must be a pair of numbers",
        min_score=1,
        only_accepted=True,
        n_results=5
    )

    print("___ RESULTS ___")
    print(results)

    for qa in results:
        print(f"Вопрос: {qa['question_title']}")
        print(f"Тело: {qa['question_body']}")
        print(f" Score: {qa['question_score']}")
        print(f" Ответ: {qa['best_answer']['score']} (accepted={qa['best_answer']['is_accepted']})")
        print(f"  {qa['url']}")
        print()


if __name__ == "__main__":
    test_get_questions_with_answers()
