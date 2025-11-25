import requests
import time
from typing import List, Dict, Any

class StackOverflowSimilarQuestions:
    def __init__(self, api_key: str = None):
        self.base_url = "https://api.stackexchange.com/2.3"
        self.api_key = api_key
        
    def get_similar_questions(self, 
                            title: str = None,
                            tags: List[str] = None,
                            n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Получение похожих вопросов по заголовку и тегам
        """
        params = {
            'order': 'desc',
            'sort': 'relevance',
            'site': 'stackoverflow',
            'filter': '!6WPIomnMOOD*e',
            'pagesize': n_results
        }
        
        if title:
            # Эндпоинт для поиска по заголовку
            url = f"{self.base_url}/search"
            params['title'] = title
            params['intitle'] = title  # Более строгий поиск в заголовке
            
        elif tags:
            # Эндпоинт для вопросов по тегам
            url = f"{self.base.url}/questions"
            params['tagged'] = ';'.join(tags)
        else:
            raise ValueError("Необходимо указать title или tags")
            
        if self.api_key:
            params['key'] = self.api_key
            
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            # return self._format_questions(data.get('items', []))
            return data.get('items', [])
        else:
            print(f"Ошибка API: {response.status_code}")
            return []
    
    def _format_questions(self, questions: List[Dict]) -> List[Dict]:
        """Форматирование результатов"""
        formatted = []
        for q in questions:
            formatted.append({
                'question_id': q['question_id'],
                'title': q['title'],
                'link': q['link'],
                'score': q['score'],
                'answer_count': q['answer_count'],
                'is_answered': q['is_answered'],
                'view_count': q['view_count'],
                'tags': q['tags'],
                'creation_date': q['creation_date']
            })
        return formatted


import requests
from typing import List, Dict, Any, Optional

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
        """
        Получение вопросов с проверенными ответами
        """
        url = f"{self.base_url}/search/advanced"
        
        params = {
            'q': query,
            'site': 'stackoverflow',
            'pagesize': n_results,
            'order': 'desc',
            'sort': 'votes',
            # 'filter': '!-MBrU_IzpJ5H-2nzyE2E*B5Qw*fsfTk5p9Ym',  # Расширенный фильтр с телами ответов
            'filter': '!6WPIomnMOOD*e',
            # 'filter': "include=answer.body&unsafe=false",
            'accepted': has_accepted_answer
        }
        
        if tags:
            params['tagged'] = ';'.join(tags)
            
        if self.api_key:
            params['key'] = self.api_key
            
        response = self.session.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            questions = data.get('items', [])
            
            # Фильтрация по минимальному score
            filtered_questions = [
                q for q in questions 
                if q['score'] >= min_score
            ]
            
            return self._enrich_with_best_answers(filtered_questions, only_accepted)
        else:
            print(f"Ошибка API: {response.status_code}")
            return []
    
    def _enrich_with_best_answers(self, 
                                questions: List[Dict], 
                                only_accepted: bool) -> List[Dict]:
        """
        Обогащение вопросов лучшими ответами
        """
        enriched_questions = []
        
        for question in questions:
            # Получаем ответы для вопроса
            answers = self._get_question_answers(question['question_id'])
            
            if not answers:
                continue
                
            # Выбираем лучший ответ
            best_answer = self._select_best_answer(answers, only_accepted)
            
            if best_answer:
                enriched_questions.append({
                    'question_id': question['question_id'],
                    'question_title': question['title'],
                    'question_body': self._clean_html(question['body']),
                    'question_score': question['score'],
                    'question_tags': question['tags'],
                    'question_views': question['view_count'],
                    'answer_count': question['answer_count'],
                    'url': question['link'],
                    'accepted_answer_id': question.get('accepted_answer_id'),
                    
                    # Данные лучшего ответа
                    'best_answer': {
                        'answer_id': best_answer['answer_id'],
                        'body': self._clean_html(best_answer['body']),
                        'score': best_answer['score'],
                        'is_accepted': best_answer['is_accepted'],
                        'owner_reputation': best_answer.get('owner', {}).get('reputation', 0)
                    }
                })
        
        return enriched_questions
    
    def _get_question_answers(self, question_id: int) -> List[Dict]:
        """
        Получение всех ответов на вопрос
        """
        url = f"{self.base_url}/questions/{question_id}/answers"
        
        params = {
            'site': 'stackoverflow',
            'order': 'desc',
            'sort': 'votes',
            # 'filter': '!-*jbN-OXKfDP',  # Фильтр с телами ответов
            'filter': '!6WPIomnMOOD*e',
            'pagesize': 20
        }
        
        if self.api_key:
            params['key'] = self.api_key
            
        response = self.session.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            # print(data.get('items', []))
            return data.get('items', [])
        else:
            return []
    
    def _select_best_answer(self, 
                          answers: List[Dict], 
                          only_accepted: bool) -> Optional[Dict]:
        """
        Выбор лучшего ответа по приоритетам:
        1. Принятый ответ (accepted)
        2. Ответ с наивысшим рейтингом
        3. Ответ от пользователя с высокой репутацией
        """
        if only_accepted:
            # Ищем принятый ответ
            accepted_answers = [a for a in answers if a.get('is_accepted', False)]
            if accepted_answers:
                return accepted_answers[0]
            return None
        
        # Если принятого ответа нет или мы не ограничиваемся только принятыми
        if answers:
            # Сортируем по рейтингу и репутации
            sorted_answers = sorted(
                answers,
                key=lambda x: (
                    x.get('score', 0),
                    x.get('owner', {}).get('reputation', 0)
                ),
                reverse=True
            )
            return sorted_answers[0]
        
        return None
    
    def _clean_html(self, html_text: str) -> str:
        """Очистка HTML контента"""
        import re
        from html import unescape
        
        # Удаляем HTML теги
        clean = re.compile('<.*?>')
        text = re.sub(clean, '', html_text)
        
        # Декодируем HTML entities
        text = unescape(text)
        
        # Убираем лишние пробелы
        text = ' '.join(text.split())
        
        return text

if __name__ == "__main__":
    # q = StackOverflowSimilarQuestions()
    # ans = q.get_similar_questions('What is difference between nn.Module and nn.Sequential')
    # print(ans)

    # Инициализация API
    so_api = StackOverflowAnswersAPI()

    # Получение проверенных ответов
    verified_answers = so_api.get_questions_with_answers(
        query="What is difference between nn.Module and nn.Sequential",
        # tags=["python", "json"],
        min_score=5,
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