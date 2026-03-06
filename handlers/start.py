from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from config import ADMIN_ID
from storage.database import is_allowed, ensure_user_profile, get_user_settings, is_admin
from keyboards.menus import main_menu_kb

router = Router()

WELCOME_TEXT = (
    "👋 Привет! Я — бот-интерфейс к Perplexity.\n\n"
    "Просто напишите мне сообщение или отправьте фото, и я передам его модели.\n\n"
    "Используйте меню ниже для управления настройками."
)

NO_ACCESS_TEXT = (
    "🚫 У вас нет доступа к боту.\n"
    "Обратитесь к администратору для получения доступа."
)


@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    if not is_allowed(user_id):
        await message.answer(NO_ACCESS_TEXT)
        return

    ensure_user_profile(
        user_id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
    )
    settings = get_user_settings(user_id)
    admin = is_admin(user_id)

    status_line = _build_status(settings)
    await message.answer(
        f"{WELCOME_TEXT}\n\n{status_line}",
        reply_markup=main_menu_kb(settings, is_admin=admin),
    )


@router.callback_query(F.data == "back_main")
async def back_to_main(callback: CallbackQuery):
    user_id = callback.from_user.id
    settings = get_user_settings(user_id)
    admin = is_admin(user_id)
    status_line = _build_status(settings)

    await callback.message.edit_text(
        f"{WELCOME_TEXT}\n\n{status_line}",
        reply_markup=main_menu_kb(settings, is_admin=admin),
    )
    await callback.answer()


def _build_status(settings: dict) -> str:
    model = settings.get("model_name", "Sonar")
    reasoning = "✅" if settings.get("reasoning") else "❌"
    web = "✅" if settings.get("web_search") else "❌"
    return f"📌 Модель: {model} | Рассуждение: {reasoning} | Поиск: {web}"
