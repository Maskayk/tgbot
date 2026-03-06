import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from storage.database import (
    is_admin,
    add_user,
    remove_user,
    get_allowed_users,
    get_user_count,
)
from keyboards.menus import admin_panel_kb, admin_back_kb

logger = logging.getLogger(__name__)
router = Router()

NOT_ADMIN_TEXT = "🚫 У вас нет доступа к админ-панели."


class AdminStates(StatesGroup):
    waiting_add_user_id = State()
    waiting_remove_user_id = State()


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer(NOT_ADMIN_TEXT)
        return
    await message.answer("🔧 Админ-панель", reply_markup=admin_panel_kb())


@router.callback_query(F.data == "admin_panel")
async def show_admin_panel(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer(NOT_ADMIN_TEXT, show_alert=True)
        return
    await state.clear()
    await callback.message.edit_text("🔧 Админ-панель", reply_markup=admin_panel_kb())
    await callback.answer()


@router.callback_query(F.data == "admin_add_user")
async def admin_add_user(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer(NOT_ADMIN_TEXT, show_alert=True)
        return
    await state.set_state(AdminStates.waiting_add_user_id)
    await callback.message.edit_text(
        "➕ Введите user_id пользователя, которому хотите выдать доступ:",
        reply_markup=admin_back_kb(),
    )
    await callback.answer()


@router.message(AdminStates.waiting_add_user_id)
async def process_add_user(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    text = message.text.strip()
    if not text.isdigit():
        await message.answer(
            "⚠️ Пожалуйста, отправьте числовой user_id.",
            reply_markup=admin_back_kb(),
        )
        return

    user_id = int(text)
    add_user(user_id)
    await state.clear()
    await message.answer(
        f"✅ Пользователь {user_id} добавлен. Доступ выдан.",
        reply_markup=admin_panel_kb(),
    )


@router.callback_query(F.data == "admin_remove_user")
async def admin_remove_user(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer(NOT_ADMIN_TEXT, show_alert=True)
        return
    await state.set_state(AdminStates.waiting_remove_user_id)
    await callback.message.edit_text(
        "➖ Введите user_id пользователя, которого хотите удалить:",
        reply_markup=admin_back_kb(),
    )
    await callback.answer()


@router.message(AdminStates.waiting_remove_user_id)
async def process_remove_user(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    text = message.text.strip()
    if not text.isdigit():
        await message.answer(
            "⚠️ Пожалуйста, отправьте числовой user_id.",
            reply_markup=admin_back_kb(),
        )
        return

    user_id = int(text)
    success = remove_user(user_id)
    await state.clear()

    if success:
        await message.answer(
            f"✅ Пользователь {user_id} удалён. Доступ закрыт.",
            reply_markup=admin_panel_kb(),
        )
    else:
        await message.answer(
            "⚠️ Невозможно удалить главного администратора.",
            reply_markup=admin_panel_kb(),
        )


@router.callback_query(F.data == "admin_list_users")
async def admin_list_users(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer(NOT_ADMIN_TEXT, show_alert=True)
        return

    users = get_allowed_users()
    if not users:
        text = "📋 Список пуст."
    else:
        lines = ["📋 Список пользователей с доступом:\n"]
        for u in users:
            uid = u.get("user_id", "?")
            name = u.get("first_name", "")
            username = u.get("username", "")
            added = u.get("added_at", "?")[:10]
            line = f"• {uid}"
            if name:
                line += f" — {name}"
            if username:
                line += f" (@{username})"
            line += f" [{added}]"
            lines.append(line)
        text = "\n".join(lines)

    await callback.message.edit_text(text, reply_markup=admin_back_kb())
    await callback.answer()


@router.callback_query(F.data == "admin_user_count")
async def admin_user_count(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer(NOT_ADMIN_TEXT, show_alert=True)
        return

    count = get_user_count()
    await callback.message.edit_text(
        f"📊 Всего пользователей с доступом: {count}",
        reply_markup=admin_back_kb(),
    )
    await callback.answer()
