from typing import Dict, List, Any
import requests
<<<<<<< HEAD:rag/so_similar_questions.py

=======
# import time
from typing import List, Dict, Any, Optional
>>>>>>> web_search:rag/so_answers.py

class StackOverflowAnswersAPI:
    def __init__(self, api_key: str = None):
        self.base_url = "https://api.stackexchange.com/2.3"
        self.api_key = api_key
        self.session = requests.Session()
    
    def get_questions_with_answers(self,
<<<<<<< HEAD:rag/so_similar_questions.py
        query: str,
        tags: List[str] = None,
        min_score: int = 5,
        only_accepted: bool = True,
        has_accepted_answer: bool = True,
        n_results: int = 10) -> List[Dict[str, Any]]:

=======
                                 query: str,
                                 tags: List[str] = None,
                                 min_score: int = 0,
                                 only_accepted: bool = True,
                                 has_accepted_answer: bool = True,
                                 n_results: int = 10,
                                 additional_question_ids: List[int] = []) -> List[Dict[str, Any]]:
        """
        Получение вопросов с проверенными ответами
        """
>>>>>>> web_search:rag/so_answers.py
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
<<<<<<< HEAD:rag/so_similar_questions.py
        
        if response.status_code != 200:
            print(f"Ошибка API: {response.status_code}")
            return []
            
        data = response.json()
        questions = data.get('items', [])
        
        filtered_questions = [q for q in questions if q['score'] >= min_score]
        
        return self._enrich_with_best_answers(filtered_questions, only_accepted)
    
    def _enrich_with_best_answers(self, questions: List[Dict], only_accepted: bool):
        enriched = []
        
        for question in questions:
=======

        # print(f"Response: {response.json()}")
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    questions = data
                else:
                    questions = data.get('items', [])
            except Exception as e:
                print(f"Ошибка при получении вопросов: {e} при ответе {response.json()}")
                return []
            # Фильтрация по минимальному score
            filtered_questions = [
                q for q in questions 
                if q['score'] >= min_score
            ]
            # print('filtered_questions ', filtered_questions)
            q_ids = [q['question_id'] for q in filtered_questions]
            print('SO Answers API returns q_ids ', q_ids)

            if additional_question_ids:
                additional_questions = self._get_questions_by_ids(additional_question_ids)
                additional_questions = [q for q in additional_questions 
                                        if q['question_id'] not in q_ids]  # Убираем дубликаты 
            filtered_questions.extend(additional_questions)
            # print('filtered_questions ', filtered_questions)
            # print('additional filtered_questions ', filtered_questions)
            # print('_____________')
            return self._enrich_with_best_answers(filtered_questions, only_accepted)
        else:
            print(f"Ошибка API: {response.status_code}")
            return []

    def _get_questions_by_ids(self, additional_question_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Получение вопросов по их идентификаторам
        """
        url_ids = [f"{self.base_url}/questions/{qid}" for qid in additional_question_ids]
        # print('url_ids ', url_ids)
        additional_questions = []
        for url_id in url_ids:

            response = self.session.get(
                url_id, 
                params={
                    'order': 'desc', 
                    'sort': 'activity', 
                    'site': 'stackoverflow', 
                    'filter': '!nNPvSNPI7A' # Фильтр с телами ответов
                    }
                    )
            # print('response ', response) 
            if response.status_code == 200:
                try:
                    data = response.json()
                    question = data.get('items', [])[0]
                    # print('question ', question)
                    additional_questions.append(question)
                except Exception as e:
                    print(f"Ошибка при получении вопроса по идентификатору {url_id}: {e}")
                    continue
            else:
                print(f"Ошибка API: {response.status_code}")
        return additional_questions


    def _enrich_with_best_answers(self, 
                                questions: List[Dict], 
                                only_accepted: bool) -> List[Dict]:
        """
        Обогащение вопросов лучшими ответами
        """
        enriched_questions = []
        
        for question in questions:
            # Получаем ответы для вопроса
            # print('question ', question)
>>>>>>> web_search:rag/so_answers.py
            answers = self._get_question_answers(question['question_id'])
            
            if not answers:
                continue
            
            best_answer = self._select_best_answer(answers, only_accepted)
            if not best_answer:
                continue
            
            enriched.append({
                'question_id': question['question_id'],
                'question_title': question['title'],
                'question_body': self._clean_html(question['body']),
                'question_score': question['score'],
                'question_tags': question['tags'],
                'question_views': question['view_count'],
                'answer_count': question['answer_count'],
                'url': question['link'],
                'accepted_answer_id': question.get('accepted_answer_id'),
                'best_answer': {
                    'answer_id': best_answer['answer_id'],
                    'body': self._clean_html(best_answer['body']),
                    'score': best_answer['score'],
                    'is_accepted': best_answer['is_accepted'],
                    'owner_reputation': best_answer.get('owner', {}).get('reputation', 0)
                }
            })

        return enriched
    
    def _get_question_answers(self, question_id: int):
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
    
    def _select_best_answer(self, answers: List[Dict], only_accepted: bool):
        """
        Выбор лучшего ответа:
        1) принятый
        2) лучший по score
        """
        if only_accepted:
            accepted = [a for a in answers if a.get('is_accepted')]
            if accepted:
                return accepted[0]
            return None
        
        # сортировка по score + репутации
        return sorted(
            answers,
            key=lambda x: (x.get('score', 0),
                x.get('owner', {}).get('reputation', 0)),
            reverse=True
        )[0]
    
    def _clean_html(self, html_text: str) -> str:
        import re
        from html import unescape
        
        clean = re.compile('<.*?>')
        text = re.sub(clean, '', html_text)
        text = unescape(text)
<<<<<<< HEAD:rag/so_similar_questions.py
        return ' '.join(text.split())
=======
        
        # Убираем лишние пробелы
        text = ' '.join(text.split())
        
        return text


def test_get_questions_with_answers():
    # q = StackOverflowSimilarQuestions()
    # ans = q.get_similar_questions('What is difference between nn.Module and nn.Sequential')
    # print(ans)

    # Инициализация API
    so_api = StackOverflowAnswersAPI()

    # Получение проверенных ответов
    verified_answers = so_api.get_questions_with_answers(
        query="center argument must be a pair of numbers",
        # tags=["python", "json"],
        min_score=1,
        only_accepted=True,
        n_results=5
    )
    print('_____________')
    print('verified_answers ', verified_answers)
    print('_____________')

    for qa in verified_answers:
        print(f"🎯 Вопрос: {qa['question_title']}. Тело вопроса:{qa['question_body']}.")
        print(f"   👍 Рейтинг вопроса: {qa['question_score']}")
        print(f"   ✅ Принятый ответ: {qa['best_answer']['is_accepted']}")
        print(f"   ⭐ Рейтинг ответа: {qa['best_answer']['score']}")
        print(f"   👤 Репутация автора: {qa['best_answer']['owner_reputation']}")
        print(f"   📝 Ответ: {qa['best_answer']['body'][:]}...")
        print(f"   🔗 Ссылка: {qa['url']}")
        print()


if __name__ == "__main__":
    test_get_questions_with_answers()
>>>>>>> web_search:rag/so_answers.py
