class BaseWebSearchEngine:
    """
    BaseWebSearchEngine — базовый класс для поиска в интернете
    Источник данных для RAG-системы (Retrieval-Augmented Generation)
    Наследуйтесь от этого класса для реализации поисковиков с конкретным API/источником
    """

    async def search(self, query, top_k=5):
        """
        Выполнить поиск по интернету по данному запросу.
        :param query: поисковый запрос пользователя
        :param top_k: сколько документов вернуть (опционально)
        :return: список результатов поиска (документов)
        """
        raise NotImplementedError("Метод search должен быть реализован в наследнике")

    def parse_results(self, raw_results):
        """
        Обработать/распарсить "сырые" результаты поиска в удобный формат для RAG.
        :param raw_results: необработанные результаты поиска/ответа API
        :return: массив структурированных документов
        """
        raise NotImplementedError("Метод parse_results должен быть реализован в наследнике")

