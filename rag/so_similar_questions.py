from typing import Dict, List, Any
import requests


class StackOverflowAnswersAPI:
    def __init__(self, api_key: str = None):
        self.base_url = "https://api.stackexchange.com/2.3"
        self.api_key = api_key
        self.session = requests.Session()
    
    def get_questions_with_answers(self,
        query: str,
        tags: List[str] = None,
        min_score: int = 5,
        only_accepted: bool = True,
        has_accepted_answer: bool = True,
        n_results: int = 10) -> List[Dict[str, Any]]:

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
            
        data = response.json()
        questions = data.get('items', [])
        
        filtered_questions = [q for q in questions if q['score'] >= min_score]
        
        return self._enrich_with_best_answers(filtered_questions, only_accepted)
    
    def _enrich_with_best_answers(self, questions: List[Dict], only_accepted: bool):
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
        return ' '.join(text.split())
