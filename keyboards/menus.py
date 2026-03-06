from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import MODELS, CATEGORY_NAMES


def main_menu_kb(settings: dict, is_admin: bool = False) -> InlineKeyboardMarkup:
    model_name = settings.get("model_name", "Sonar")
    reasoning = settings.get("reasoning", False)
    reasoning_icon = "✅" if reasoning else "❌"

    buttons = [
        [InlineKeyboardButton(text=f"🤖 Модель: {model_name}", callback_data="menu_models")],
        [InlineKeyboardButton(text=f"💭 Рассуждение: {reasoning_icon}", callback_data="toggle_reasoning")],
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="menu_settings")],
        [InlineKeyboardButton(text="🆕 Новая тема", callback_data="new_topic")],
        [InlineKeyboardButton(text="❓ Помощь", callback_data="help")],
    ]

    if is_admin:
        buttons.append([InlineKeyboardButton(text="🔧 Админ-панель", callback_data="admin_panel")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def model_categories_kb() -> InlineKeyboardMarkup:
    buttons = []
    for cat_id, cat_name in CATEGORY_NAMES.items():
        buttons.append([InlineKeyboardButton(text=cat_name, callback_data=f"cat_{cat_id}")])
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def model_list_kb(category: str) -> InlineKeyboardMarkup:
    models = MODELS.get(category, [])
    buttons = []
    for m in models:
        buttons.append([InlineKeyboardButton(text=m["name"], callback_data=f"model_{m['id']}_{category}")])
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="menu_models")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def settings_kb(settings: dict) -> InlineKeyboardMarkup:
    temp = settings.get("temperature", 0.7)
    max_tok = settings.get("max_tokens", 4096)
    effort = settings.get("reasoning_effort", "medium")
    web = settings.get("web_search", True)
    web_icon = "✅" if web else "❌"

    buttons = [
        [InlineKeyboardButton(text=f"🌡 Температура: {temp}", callback_data="set_temperature")],
        [InlineKeyboardButton(text=f"📏 Макс. токенов: {max_tok}", callback_data="set_max_tokens")],
        [InlineKeyboardButton(text=f"🧠 Усилие рассуждения: {effort}", callback_data="set_reasoning_effort")],
        [InlineKeyboardButton(text=f"🌐 Веб-поиск: {web_icon}", callback_data="toggle_web_search")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def temperature_kb() -> InlineKeyboardMarkup:
    values = [0.1, 0.3, 0.5, 0.7, 0.9, 1.0]
    buttons = []
    row = []
    for v in values:
        row.append(InlineKeyboardButton(text=str(v), callback_data=f"temp_{v}"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="menu_settings")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def max_tokens_kb() -> InlineKeyboardMarkup:
    values = [1024, 2048, 4096, 8192, 16384]
    buttons = []
    row = []
    for v in values:
        row.append(InlineKeyboardButton(text=str(v), callback_data=f"maxtok_{v}"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="menu_settings")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def reasoning_effort_kb() -> InlineKeyboardMarkup:
    efforts = [("low", "Низкое"), ("medium", "Среднее"), ("high", "Высокое")]
    buttons = []
    for val, label in efforts:
        buttons.append([InlineKeyboardButton(text=label, callback_data=f"effort_{val}")])
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="menu_settings")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def help_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")],
    ])


def confirm_new_topic_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да, сбросить", callback_data="confirm_new_topic"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="back_main"),
        ],
    ])


# --- Admin keyboards ---

def admin_panel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить пользователя", callback_data="admin_add_user")],
        [InlineKeyboardButton(text="➖ Удалить пользователя", callback_data="admin_remove_user")],
        [InlineKeyboardButton(text="📋 Список пользователей", callback_data="admin_list_users")],
        [InlineKeyboardButton(text="📊 Количество пользователей", callback_data="admin_user_count")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")],
    ])


def admin_back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад в админку", callback_data="admin_panel")],
    ])
