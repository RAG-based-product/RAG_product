# backend/backend_core.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import logging
import os
from dotenv import load_dotenv
from agents.agent_bot_core import AgentBot
from models.mistral_llm_client import MistralLLMClient
from web_search.tavily_web_search import TavilyWebSearchEngine

logger = logging.getLogger(__name__)

app = FastAPI(title="RAG API")

# Глобальная переменная для RAG-сервиса
rag_service: AgentBot = None

@app.on_event("startup")
async def startup_event():
    """Инициализация RAG-сервиса при запуске приложения."""
    global rag_service
    
    # Загрузка переменных окружения
    load_dotenv()
    
    # Проверка необходимых ключей
    if not os.getenv("MISTRAL_API_KEY"):
        logger.error("MISTRAL_API_KEY не найден в переменных окружения")
        raise RuntimeError("MISTRAL_API_KEY не настроен")
    
    if not os.getenv("TAVILY_API_KEY"):
        logger.warning("TAVILY_API_KEY не найден, веб-поиск может не работать")
    
    # Инициализация зависимостей
    logger.info("Инициализация Mistral LLM Client...")
    llm = MistralLLMClient()
    
    logger.info("Инициализация Tavily Web Search Engine...")
    web_search_engine = TavilyWebSearchEngine()
    
    # Создание RAG-сервиса с передачей всех зависимостей
    system_prompt = "Вы — экспертный ассистент RAG. Отвечайте на вопросы на основе предоставленного контекста."
    rag_service = AgentBot(
        name="rag_agent",
        llm_client=llm,
        system_prompt=system_prompt,
        web_search_engine=web_search_engine
    )
    
    logger.info("RAG Service успешно инициализирован")

# Модели запроса/ответа
class UserRequest(BaseModel):
    prompt: str

class SourceResponse(BaseModel):
    title: str
    url: str
    content: str

class AnswerResponse(BaseModel):
    text: str
    sources: List[SourceResponse]

@app.post("/generate_response", response_model=AnswerResponse)
async def generate_response(req: UserRequest) -> AnswerResponse:
    """
    Получает запрос пользователя, обрабатывает через RAG и возвращает ответ.
    """
    if rag_service is None:
        raise HTTPException(status_code=503, detail="RAG Service не инициализирован")
    
    try:
        # Вызываем RAG-сервис
        result = await rag_service.process(req.prompt)
        
        # Извлекаем ответ и источники из словаря
        answer_text = result.get("answer", "")
        sources = result.get("sources", [])
        
        # Преобразуем источники в формат ответа
        sources_response = [
            SourceResponse(
                title=source.title if hasattr(source, 'title') else source.get('title', ''),
                url=source.url if hasattr(source, 'url') else source.get('url', ''),
                content=source.content if hasattr(source, 'content') else source.get('content', '')
            )
            for source in sources
        ]
        
        return AnswerResponse(text=answer_text, sources=sources_response)
        
    except Exception as e:
        logger.error(f"Ошибка при обработке запроса: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка обработки: {str(e)}")

@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса."""
    return {"status": "ok", "rag_service_initialized": rag_service is not None}