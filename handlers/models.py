from aiogram import Router, F
from aiogram.types import CallbackQuery

from config import MODELS, CATEGORY_NAMES
from storage.database import get_user_settings, update_user_settings
from keyboards.menus import model_categories_kb, model_list_kb

router = Router()


@router.callback_query(F.data == "menu_models")
async def show_model_categories(callback: CallbackQuery):
    settings = get_user_settings(callback.from_user.id)
    current = settings.get("model_name", "Sonar")
    await callback.message.edit_text(
        f"🤖 Выберите категорию моделей\n\nТекущая модель: {current}",
        reply_markup=model_categories_kb(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("cat_"))
async def show_models_in_category(callback: CallbackQuery):
    category = callback.data.replace("cat_", "")
    cat_name = CATEGORY_NAMES.get(category, category)
    await callback.message.edit_text(
        f"{cat_name} — выберите модель:",
        reply_markup=model_list_kb(category),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("model_"))
async def select_model(callback: CallbackQuery):
    parts = callback.data.split("_", 2)
    # model_{id}_{category}
    model_id = parts[1]
    category = parts[2] if len(parts) > 2 else ""

    # Find model info
    model_info = None
    for cat_models in MODELS.values():
        for m in cat_models:
            if m["id"] == model_id:
                model_info = m
                break
        if model_info:
            break

    if not model_info:
        await callback.answer("Модель не найдена", show_alert=True)
        return

    update_user_settings(
        callback.from_user.id,
        model_id=model_info["id"],
        model_name=model_info["name"],
        model_supports_reasoning=model_info["reasoning"],
    )

    # If model doesn't support reasoning, disable it
    if not model_info["reasoning"]:
        update_user_settings(callback.from_user.id, reasoning=False)

    await callback.answer(f"Выбрана модель: {model_info['name']}", show_alert=True)

    # Go back to categories
    settings = get_user_settings(callback.from_user.id)
    current = settings.get("model_name", "Sonar")
    await callback.message.edit_text(
        f"🤖 Выберите категорию моделей\n\nТекущая модель: {current}",
        reply_markup=model_categories_kb(),
    )
