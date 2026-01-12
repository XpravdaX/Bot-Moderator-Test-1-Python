from telebot import types


def get_admin_keyboard():
    """Клавиатура для администраторов"""
    keyboard = types.InlineKeyboardMarkup(row_width=2)

    buttons = [
        types.InlineKeyboardButton("📊 Статистика", callback_data="admin_stats"),
        types.InlineKeyboardButton("📝 Слова", callback_data="admin_words"),
        types.InlineKeyboardButton("👤 Пользователи", callback_data="admin_users"),
        types.InlineKeyboardButton("⚙️ Настройки", callback_data="admin_settings"),
        types.InlineKeyboardButton("📋 Логи", callback_data="admin_logs")
    ]

    keyboard.add(*buttons)
    return keyboard


def get_main_keyboard():
    """Основная клавиатура"""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    buttons = [
        types.KeyboardButton("/help"),
        types.KeyboardButton("/rules"),
        types.KeyboardButton("/stats"),
        types.KeyboardButton("/report")
    ]

    keyboard.add(*buttons)
    return keyboard


def get_moderation_keyboard(user_id):
    """Клавиатура для действий модерации"""
    keyboard = types.InlineKeyboardMarkup(row_width=3)

    buttons = [
        types.InlineKeyboardButton("⚠️ Предупредить", callback_data=f"warn_{user_id}"),
        types.InlineKeyboardButton("🔇 Мут 1ч", callback_data=f"mute_1h_{user_id}"),
        types.InlineKeyboardButton("🔇 Мут 24ч", callback_data=f"mute_24h_{user_id}"),
        types.InlineKeyboardButton("⛔ Бан", callback_data=f"ban_{user_id}"),
        types.InlineKeyboardButton("✅ Простить", callback_data=f"forgive_{user_id}"),
        types.InlineKeyboardButton("📝 Подробно", callback_data=f"details_{user_id}")
    ]

    keyboard.add(*buttons[0:3])
    keyboard.add(*buttons[3:6])
    return keyboard