from aiogram import Router, F
from aiogram.types import CallbackQuery

from storage.database import get_user_settings, update_user_settings, clear_history
from keyboards.menus import (
    settings_kb,
    temperature_kb,
    max_tokens_kb,
    reasoning_effort_kb,
    help_kb,
    confirm_new_topic_kb,
)

router = Router()


@router.callback_query(F.data == "toggle_reasoning")
async def toggle_reasoning(callback: CallbackQuery):
    user_id = callback.from_user.id
    settings = get_user_settings(user_id)

    if not settings.get("model_supports_reasoning", False):
        await callback.answer(
            "⚠️ Текущая модель не поддерживает режим рассуждения. Выберите модель из категории «Думающие».",
            show_alert=True,
        )
        return

    new_val = not settings.get("reasoning", False)
    update_user_settings(user_id, reasoning=new_val)
    status = "включено ✅" if new_val else "выключено ❌"
    await callback.answer(f"Рассуждение {status}", show_alert=True)

    # Refresh main menu
    from handlers.start import _build_status, WELCOME_TEXT
    from keyboards.menus import main_menu_kb
    from storage.database import is_admin

    settings = get_user_settings(user_id)
    admin = is_admin(user_id)
    status_line = _build_status(settings)
    await callback.message.edit_text(
        f"{WELCOME_TEXT}\n\n{status_line}",
        reply_markup=main_menu_kb(settings, is_admin=admin),
    )


@router.callback_query(F.data == "menu_settings")
async def show_settings(callback: CallbackQuery):
    settings = get_user_settings(callback.from_user.id)
    await callback.message.edit_text(
        "⚙️ Настройки генерации\n\nВыберите параметр для изменения:",
        reply_markup=settings_kb(settings),
    )
    await callback.answer()


@router.callback_query(F.data == "set_temperature")
async def set_temperature(callback: CallbackQuery):
    await callback.message.edit_text(
        "🌡 Выберите температуру:\n\nНиже — точнее, выше — креативнее.",
        reply_markup=temperature_kb(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("temp_"))
async def apply_temperature(callback: CallbackQuery):
    val = float(callback.data.replace("temp_", ""))
    update_user_settings(callback.from_user.id, temperature=val)
    await callback.answer(f"Температура установлена: {val}", show_alert=True)
    settings = get_user_settings(callback.from_user.id)
    await callback.message.edit_text(
        "⚙️ Настройки генерации\n\nВыберите параметр для изменения:",
        reply_markup=settings_kb(settings),
    )


@router.callback_query(F.data == "set_max_tokens")
async def set_max_tokens(callback: CallbackQuery):
    await callback.message.edit_text(
        "📏 Выберите максимальное количество токенов:",
        reply_markup=max_tokens_kb(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("maxtok_"))
async def apply_max_tokens(callback: CallbackQuery):
    val = int(callback.data.replace("maxtok_", ""))
    update_user_settings(callback.from_user.id, max_tokens=val)
    await callback.answer(f"Макс. токенов: {val}", show_alert=True)
    settings = get_user_settings(callback.from_user.id)
    await callback.message.edit_text(
        "⚙️ Настройки генерации\n\nВыберите параметр для изменения:",
        reply_markup=settings_kb(settings),
    )


@router.callback_query(F.data == "set_reasoning_effort")
async def set_reasoning_effort(callback: CallbackQuery):
    await callback.message.edit_text(
        "🧠 Выберите уровень усилия рассуждения:",
        reply_markup=reasoning_effort_kb(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("effort_"))
async def apply_reasoning_effort(callback: CallbackQuery):
    val = callback.data.replace("effort_", "")
    update_user_settings(callback.from_user.id, reasoning_effort=val)
    labels = {"low": "Низкое", "medium": "Среднее", "high": "Высокое"}
    await callback.answer(f"Усилие: {labels.get(val, val)}", show_alert=True)
    settings = get_user_settings(callback.from_user.id)
    await callback.message.edit_text(
        "⚙️ Настройки генерации\n\nВыберите параметр для изменения:",
        reply_markup=settings_kb(settings),
    )


@router.callback_query(F.data == "toggle_web_search")
async def toggle_web_search(callback: CallbackQuery):
    user_id = callback.from_user.id
    settings = get_user_settings(user_id)
    new_val = not settings.get("web_search", True)
    update_user_settings(user_id, web_search=new_val)
    status = "включён ✅" if new_val else "выключен ❌"
    await callback.answer(f"Веб-поиск {status}", show_alert=True)
    settings = get_user_settings(user_id)
    await callback.message.edit_text(
        "⚙️ Настройки генерации\n\nВыберите параметр для изменения:",
        reply_markup=settings_kb(settings),
    )


@router.callback_query(F.data == "new_topic")
async def new_topic_confirm(callback: CallbackQuery):
    await callback.message.edit_text(
        "🆕 Начать новую тему?\n\nИстория текущего диалога будет удалена.",
        reply_markup=confirm_new_topic_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "confirm_new_topic")
async def confirm_new_topic(callback: CallbackQuery):
    clear_history(callback.from_user.id)
    await callback.answer("✅ Тема сброшена!", show_alert=True)

    from handlers.start import _build_status, WELCOME_TEXT
    from keyboards.menus import main_menu_kb
    from storage.database import is_admin

    settings = get_user_settings(callback.from_user.id)
    admin = is_admin(callback.from_user.id)
    status_line = _build_status(settings)
    await callback.message.edit_text(
        f"{WELCOME_TEXT}\n\n{status_line}",
        reply_markup=main_menu_kb(settings, is_admin=admin),
    )


@router.callback_query(F.data == "help")
async def show_help(callback: CallbackQuery):
    help_text = (
        "❓ *Помощь*\n\n"
        "Просто отправьте мне текстовое сообщение или фото — я передам его в Perplexity "
        "и верну ответ\\.\n\n"
        "🤖 *Модель* — выберите AI\\-модель для ответов\n"
        "💭 *Рассуждение* — включает режим глубокого анализа \\(для поддерживаемых моделей\\)\n"
        "⚙️ *Настройки* — температура, токены и другие параметры\n"
        "🆕 *Новая тема* — сбросить историю диалога\n\n"
        "📸 Отправьте фото с подписью или без — бот проанализирует изображение\\."
    )
    await callback.message.edit_text(
        help_text,
        reply_markup=help_kb(),
        parse_mode="MarkdownV2",
    )
    await callback.answer()
