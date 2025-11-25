from rag.so_similar_questions import StackOverflowAnswersAPI

def get_prompt(user_content):
    # TODO:
    so_api = StackOverflowAnswersAPI()

    # Получение проверенных ответов
    verified_answers = so_api.get_questions_with_answers(
        query=user_content,
        # tags=["python", "json"],
        min_score=5,
        only_accepted=True,
        n_results=5
    )
    rag_add = ''
    for qa in verified_answers:
        rag_add += (f"🎯 Вопрос: {qa['question_title']}. Тело вопроса:{qa['question_body']}.")
        rag_add += (f"   👍 Рейтинг вопроса: {qa['question_score']}")
        rag_add += (f"   ✅ Принятый ответ: {qa['best_answer']['is_accepted']}")
        rag_add += (f"   ⭐ Рейтинг ответа: {qa['best_answer']['score']}")
        rag_add += (f"   👤 Репутация автора: {qa['best_answer']['owner_reputation']}")
        rag_add += (f"   📝 Ответ: {qa['best_answer']['body'][:]}...")
        rag_add += (f"   🔗 Ссылка: {qa['url']}")

    message=[
            {
                "role": "system",
                "content": """
                    Объясни пользователю причину ошибки и предложи конкретное решение. Приведи пример кода и добавь ссылки на источники.
                """ + rag_add
            },
            {"role": "user", "content": user_content}
        ]

    return message

# if __name__ == "__main__":
#     get_prompt("What is difference between nn.Module and nn.Sequential")