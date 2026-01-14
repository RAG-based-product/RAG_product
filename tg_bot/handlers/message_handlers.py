from typing import List
from telegram.ext import MessageHandler as TgMessageHandler, filters
from telegram.ext import ContextTypes
from telegram import Update
from telegram.error import TimedOut

import httpx
import logging
import html

logger = logging.getLogger(__name__)

class MessageHandler:
    """
    Управляет текстовыми сообщениями, отправляет запросы на FastAPI
    и форматирует ответ для пользователя.
    """
    
    def __init__(self, api_url: str):
        """
        Args:
            api_url: URL FastAPI сервиса (например, "http://localhost:8000")
        """
        self.api_url = api_url

    async def _fetch_response(self, user_message: str) -> tuple[str, List[dict]]:
        """
        Отправляет запрос на FastAPI и возвращает ответ.
        Возвращает: (ответ_текст, список_источников)
        """
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.api_url}/generate_response",
                    json={"prompt": user_message}
                )
                response.raise_for_status()
                data = response.json()
                
                return data.get("text", ""), data.get("sources", [])
                
        except httpx.HTTPError as e:
            logger.error(f"Ошибка HTTP при запросе к FastAPI: {e}")
            return "Ошибка при обращении к серверу. Попробуйте позже.", []
        except Exception as e:
            logger.error(f"Неожиданная ошибка: {e}")
            return "Произошла внутренняя ошибка.", []

    async def _callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Асинхронный метод обратного вызова для обработки сообщения."""
        await update.message.chat.send_action(action="typing")
        user_message = update.message.text

        # Получаем информацию о пользователе
        user = update.effective_user
        user_id = user.id
        user_name = user.first_name
        username = user.username  # Может быть None
        logger.info(f"Получено сообщение от {user_name} ({username}, {user_id}): {user_message}")

        # Отправляем временное сообщение о начале поиска
        status_message = None
        try:
            status_message = await update.message.reply_text("🔍 Начинаю поиск информации, мне нужно немного времени...")
        except Exception as e:
            logger.warning(f"Не удалось отправить статусное сообщение: {e}")

        try:
            # Получение ответа от FastAPI
            llm_response, sources = await self._fetch_response(user_message)
            logger.info("llm_response, sources получены")

            # Удаляем временное сообщение о поиске
            if status_message:
                try:
                    import asyncio
                    # Анимация: меняем текст перед удалением
                    await status_message.edit_text("✅ Поиск завершен...")
                    await asyncio.sleep(0.5)
                    await status_message.edit_text("✅ Готово!")
                    await asyncio.sleep(0.5)
                    await status_message.delete()
                except Exception as e:
                    logger.warning(f"Не удалось удалить статусное сообщение: {e}")


            # Форматирование источников
            if sources:
                source_links = "\n\n<b>Источники:</b>\n"
                for i, source in enumerate(sources[:5]):
                    if isinstance(source, dict):
                        url = source.get('url', '#')
                        title = source.get('title', 'Без заголовка')
                    else:
                        url = getattr(source, 'url', '#')
                        title = getattr(source, 'title', 'Без заголовка')
                    
                    # source_links += f"{i+1}. <a href='{url}'>{title}</a>\n"
                    
                    # Экранируем HTML-специальные символы в заголовке
                    title_escaped = html.escape(str(title))
                    # URL не нужно экранировать, Telegram обработает их правильно
                    source_links += f"{i+1}. <a href='{url}'>{title_escaped}</a>\n"

                
                final_response = f"{html.escape(llm_response)}{source_links}"
                parse_mode = "HTML"
            else:
                final_response = llm_response
                parse_mode = None

        except Exception as e:
            logger.error(f"Критическая ошибка: {e}", exc_info=True)
            final_response = "К сожалению, при обработке вашего запроса произошла ошибка."
            parse_mode = None

        # Проверка длины сообщения перед отправкой
        message_length = len(final_response)
        logger.info(f"Длина сообщения перед отправкой: {message_length} символов")

        # Обработка отправки сообщения с проверкой таймаута
        try: 
            await update.message.reply_text(final_response, parse_mode=parse_mode)
        except TimedOut as e:
            logger.error(f"Таймаут при отправке сообщения в Telegram: {e}", exc_info=True)
            try:
                # Пытаемся отправить упрощенное сообщение об ошибке
                await update.message.reply_text(
                    "⚠️ Произошла ошибка при отправке ответа (таймаут). "
                    "Ответ слишком длинный или произошла проблема с сетью. "
                    "Попробуйте переформулировать запрос."
                )
            except Exception as fallback_error:
                logger.error(f"Не удалось отправить даже сообщение об ошибке: {fallback_error}")

    def register_handlers(self, application):
        """Регистрирует обработчик сообщений."""
        application.add_handler(
            TgMessageHandler(
                filters.TEXT & (~filters.COMMAND),
                self._callback
            )
        )