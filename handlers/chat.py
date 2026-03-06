import io
import logging

from aiogram import Router, F, Bot
from aiogram.types import Message

from storage.database import (
    is_allowed,
    get_user_settings,
    get_user_history,
    add_to_history,
)
from services.perplexity import (
    chat_completion,
    build_messages_text,
    build_messages_with_image,
)

logger = logging.getLogger(__name__)
router = Router()

NO_ACCESS_TEXT = "🚫 У вас нет доступа к боту. Обратитесь к администратору."
DEFAULT_IMAGE_PROMPT = "Опиши это изображение подробно."


@router.message(F.photo)
async def handle_photo(message: Message, bot: Bot):
    user_id = message.from_user.id
    if not is_allowed(user_id):
        await message.answer(NO_ACCESS_TEXT)
        return

    prompt = message.caption or DEFAULT_IMAGE_PROMPT
    settings = get_user_settings(user_id)

    waiting = await message.answer("⏳ Обрабатываю изображение...")

    try:
        # Download photo (largest size)
        photo = message.photo[-1]
        file = await bot.get_file(photo.file_id)
        buf = io.BytesIO()
        await bot.download_file(file.file_path, buf)
        image_data = buf.getvalue()

        history = get_user_history(user_id)
        messages = build_messages_with_image(prompt, image_data, history)

        result = await chat_completion(
            messages=messages,
            model=settings["model_id"],
            temperature=settings["temperature"],
            top_p=settings["top_p"],
            max_tokens=settings["max_tokens"],
            reasoning=settings["reasoning"],
            reasoning_effort=settings["reasoning_effort"],
            web_search=settings.get("web_search", True),
        )

        if result.get("error"):
            await waiting.edit_text(f"❌ {result['message']}")
            return

        content = result["content"]

        # Save to history (store text representation only for history)
        add_to_history(user_id, "user", f"[Фото] {prompt}")
        add_to_history(user_id, "assistant", content)

        response_text = _format_response(content, result.get("citations"))
        await _send_long_message(waiting, response_text)

    except Exception as e:
        logger.error("Error handling photo: %s", e)
        await waiting.edit_text("❌ Произошла ошибка при обработке изображения.")


@router.message(F.text)
async def handle_text(message: Message):
    user_id = message.from_user.id
    if not is_allowed(user_id):
        await message.answer(NO_ACCESS_TEXT)
        return

    text = message.text.strip()
    if not text:
        return

    # Ignore commands (they are handled by other routers)
    if text.startswith("/"):
        return

    settings = get_user_settings(user_id)
    waiting = await message.answer("⏳ Думаю...")

    try:
        history = get_user_history(user_id)
        messages = build_messages_text(text, history)

        result = await chat_completion(
            messages=messages,
            model=settings["model_id"],
            temperature=settings["temperature"],
            top_p=settings["top_p"],
            max_tokens=settings["max_tokens"],
            reasoning=settings["reasoning"],
            reasoning_effort=settings["reasoning_effort"],
            web_search=settings.get("web_search", True),
        )

        if result.get("error"):
            await waiting.edit_text(f"❌ {result['message']}")
            return

        content = result["content"]
        add_to_history(user_id, "user", text)
        add_to_history(user_id, "assistant", content)

        response_text = _format_response(content, result.get("citations"))
        await _send_long_message(waiting, response_text)

    except Exception as e:
        logger.error("Error handling text message: %s", e)
        await waiting.edit_text("❌ Произошла ошибка при обработке запроса.")


def _format_response(content: str, citations: list | None) -> str:
    text = content
    if citations:
        text += "\n\n📎 *Источники:*\n"
        for i, url in enumerate(citations, 1):
            text += f"{i}. {url}\n"
    return text


async def _send_long_message(waiting_msg: Message, text: str) -> None:
    """Edit waiting message or send multiple messages if text is too long."""
    max_len = 4096
    if len(text) <= max_len:
        try:
            await waiting_msg.edit_text(text)
        except Exception:
            # If edit fails (e.g., message too old), send new
            await waiting_msg.answer(text)
        return

    # Split into chunks
    chunks = []
    while text:
        if len(text) <= max_len:
            chunks.append(text)
            break
        # Find a good split point
        split_at = text.rfind("\n", 0, max_len)
        if split_at == -1:
            split_at = max_len
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n")

    # Edit first message, send rest as new messages
    await waiting_msg.edit_text(chunks[0])
    for chunk in chunks[1:]:
        await waiting_msg.answer(chunk)
