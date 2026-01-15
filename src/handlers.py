import logging
import time
from datetime import datetime, timedelta
from telebot import TeleBot, types
from config import Config
from database import db
from filters import word_filter
from keyboards import get_admin_keyboard, get_main_keyboard, get_moderation_keyboard

logger = logging.getLogger(__name__)


class MessageHandler:
    def __init__(self, bot: TeleBot):
        self.bot = bot
        self.setup_handlers()

    def setup_handlers(self):
        """Настройка обработчиков"""

        # Команды
        @self.bot.message_handler(commands=['start'])
        def start_command(message):
            self.handle_start(message)

        @self.bot.message_handler(commands=['help'])
        def help_command(message):
            self.handle_help(message)

        @self.bot.message_handler(commands=['rules'])
        def rules_command(message):
            self.handle_rules(message)

        @self.bot.message_handler(commands=['stats'])
        def stats_command(message):
            self.handle_stats(message)

        @self.bot.message_handler(commands=['report'])
        def report_command(message):
            self.handle_report(message)

        @self.bot.message_handler(commands=['admin'])
        def admin_command(message):
            self.handle_admin_panel(message)

        # Административные команды
        @self.bot.message_handler(commands=['addword'])
        def add_word_command(message):
            self.handle_add_word(message)

        @self.bot.message_handler(commands=['delword'])
        def delete_word_command(message):
            self.handle_delete_word(message)

        @self.bot.message_handler(commands=['warn'])
        def warn_user_command(message):
            self.handle_warn_user(message)

        @self.bot.message_handler(commands=['mute'])
        def mute_user_command(message):
            self.handle_mute_user(message)

        @self.bot.message_handler(commands=['unban'])
        def unban_user_command(message):
            self.handle_unban_user(message)

        # Обработка всех сообщений
        @self.bot.message_handler(func=lambda m: True, content_types=['text'])
        def handle_all_messages(message):
            self.process_message(message)

        # Новые участники
        @self.bot.message_handler(content_types=['new_chat_members'])
        def handle_new_members(message):
            self.welcome_new_member(message)

        # Callback-запросы
        @self.bot.callback_query_handler(func=lambda call: True)
        def handle_callback(call):
            self.process_callback(call)

    def handle_start(self, message):
        """Обработка команды /start"""
        user = message.from_user
        db.add_user(user.id, user.username, user.first_name, user.last_name)

        welcome_text = """
🤖 **Умный бот-модератор v1.0**

🔒 **Основные функции:**
• Автоматическая фильтрация мата и оскорблений
• Умный поиск с учетом замен букв
• Система предупреждений и наказаний
• Полное логирование действий

📋 **Для администраторов:**
Панель управления с расширенной статистикой
и настройками фильтрации.

Используйте /help для списка команд.
        """

        self.bot.send_message(
            message.chat.id,
            welcome_text,
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )

    def handle_help(self, message):
        """Обработка команды /help"""
        help_text = """
📚 **Список команд:**

**Для всех пользователей:**
/start - Начало работы с ботом
/help - Показать это сообщение
/rules - Правила чата
/stats - Статистика бота
/report [причина] - Пожаловаться на сообщение

**Для администраторов:**
/admin - Панель управления
/addword [слово] - Добавить слово в фильтр
/delword [слово] - Удалить слово из фильтра
/warn @username - Выдать предупреждение
/mute @username [время] - Заглушить пользователя
/unban @username - Разбанить пользователя

**Модерация работает автоматически:**
• Сообщения с матом удаляются
• За оскорбления выдаются предупреждения
• При повторных нарушениях - мут или бан
        """

        self.bot.send_message(message.chat.id, help_text, parse_mode='Markdown')

    def handle_rules(self, message):
        """Обработка команды /rules"""
        rules_text = """
📜 **Правила чата:**

1. **Запрещено:**
   • Нецензурная лексика и мат
   • Оскорбления участников
   • Разжигание ненависти
   • Спам и флуд
   • Реклама без согласия

2. **Наказания:**
   • 1-2 нарушения: предупреждение
   • 3 нарушения: мут 1 час
   • 4 нарушения: мут 24 часа
   • 5+ нарушений: бан

3. **Апелляции:**
   Для обжалования наказания свяжитесь с администратором.

⚠️ **Автомодерация активна 24/7**
        """

        self.bot.send_message(message.chat.id, rules_text, parse_mode='Markdown')

    def handle_stats(self, message):
        """Обработка команды /stats"""
        stats = db.get_moderation_stats()

        stats_text = f"""
📊 **Статистика бота:**

**Общая:**
• Всего действий модерации: {stats['total_actions']}
• Пользователей в базе: {stats['unique_users']}
• Кастомных слов: {stats['custom_words']}

**Фильтрация:**
• Базовых слов: {len(word_filter.base_words)}
• Активных паттернов: {len(word_filter.patterns)}
• Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M')}

**Система:**
• База данных: SQLite
• Логирование: включено
• Автообновление: каждые 24 часа
        """

        self.bot.send_message(message.chat.id, stats_text, parse_mode='Markdown')

    def handle_admin_panel(self, message):
        """Обработка команды /admin"""
        # Проверяем права администратора
        try:
            member = self.bot.get_chat_member(message.chat.id, message.from_user.id)
            if member.status not in ['creator', 'administrator']:
                self.bot.reply_to(message, "❌ Эта команда только для администраторов!")
                return
        except:
            self.bot.reply_to(message, "❌ Не удалось проверить права доступа!")
            return

        admin_text = """
⚙️ **Панель управления администратора**

Выберите действие:
        """

        self.bot.send_message(
            message.chat.id,
            admin_text,
            parse_mode='Markdown',
            reply_markup=get_admin_keyboard()
        )

    def handle_add_word(self, message):
        """Обработка команды /addword"""
        # Проверяем права администратора
        try:
            member = self.bot.get_chat_member(message.chat.id, message.from_user.id)
            if member.status not in ['creator', 'administrator']:
                self.bot.reply_to(message, "❌ Эта команда только для администраторов!")
                return
        except:
            self.bot.reply_to(message, "❌ Не удалось проверить права доступа!")
            return

        # Извлекаем слово из сообщения
        parts = message.text.split(' ', 1)
        if len(parts) < 2:
            self.bot.reply_to(message, "❌ Использование: `/addword слово`", parse_mode='Markdown')
            return

        word = parts[1].strip().lower()
        if len(word) < 2:
            self.bot.reply_to(message, "❌ Слово слишком короткое!")
            return

        # Добавляем слово в базу данных
        added = db.add_custom_word(word, message.from_user.id)
        if added:
            # Обновляем фильтр
            word_filter.load_words()
            self.bot.reply_to(message, f"✅ Слово `{word}` успешно добавлено в фильтр!", parse_mode='Markdown')
        else:
            self.bot.reply_to(message, f"❌ Слово `{word}` уже есть в фильтре!", parse_mode='Markdown')

    def handle_delete_word(self, message):
        """Обработка команды /delword"""
        # Проверяем права администратора
        try:
            member = self.bot.get_chat_member(message.chat.id, message.from_user.id)
            if member.status not in ['creator', 'administrator']:
                self.bot.reply_to(message, "❌ Эта команда только для администраторов!")
                return
        except:
            self.bot.reply_to(message, "❌ Не удалось проверить права доступа!")
            return

        # Извлекаем слово из сообщения
        parts = message.text.split(' ', 1)
        if len(parts) < 2:
            self.bot.reply_to(message, "❌ Использование: `/delword слово`", parse_mode='Markdown')
            return

        word = parts[1].strip().lower()

        # Удаляем слово из базы данных
        try:
            cursor = db.conn.cursor()
            cursor.execute('UPDATE custom_words SET is_active = FALSE WHERE word = ?', (word,))
            db.conn.commit()

            if cursor.rowcount > 0:
                # Обновляем фильтр
                word_filter.load_words()
                self.bot.reply_to(message, f"✅ Слово `{word}` успешно удалено из фильтра!", parse_mode='Markdown')
            else:
                self.bot.reply_to(message, f"❌ Слово `{word}` не найдено в фильтре!", parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Ошибка при удалении слова: {e}")
            self.bot.reply_to(message, "❌ Ошибка при удалении слова!")

    def handle_warn_user(self, message):
        """Обработка команды /warn"""
        # Проверяем права администратора
        try:
            member = self.bot.get_chat_member(message.chat.id, message.from_user.id)
            if member.status not in ['creator', 'administrator']:
                self.bot.reply_to(message, "❌ Эта команда только для администраторов!")
                return
        except:
            self.bot.reply_to(message, "❌ Не удалось проверить права доступа!")
            return

        # Извлекаем username из сообщения
        parts = message.text.split(' ', 1)
        if len(parts) < 2:
            self.bot.reply_to(message, "❌ Использование: `/warn @username`", parse_mode='Markdown')
            return

        username = parts[1].strip()
        if not username.startswith('@'):
            self.bot.reply_to(message, "❌ Укажите username в формате @username")
            return

        # Получаем ID пользователя по username
        try:
            chat_members = self.bot.get_chat_administrators(message.chat.id)
            target_user = None

            for member in chat_members:
                if member.user.username and member.user.username.lower() == username[1:].lower():
                    target_user = member.user
                    break

            if not target_user:
                # Попробуем поискать среди участников
                try:
                    # В некоторых случаях может потребоваться другие методы поиска
                    # Для упрощения пока просто сообщим об ошибке
                    self.bot.reply_to(message, f"❌ Пользователь {username} не найден в чате!")
                    return
                except:
                    self.bot.reply_to(message, f"❌ Пользователь {username} не найден в чате!")
                    return

            # Увеличиваем предупреждения
            user_data = db.get_user(target_user.id)
            current_warnings = user_data[4] if user_data else 0
            db.update_warnings(target_user.id, current_warnings + 1)

            # Определяем наказание
            punishment = self.get_punishment(current_warnings + 1)

            # Применяем наказание
            self.apply_punishment(message.chat.id, target_user.id, current_warnings + 1, punishment)

            # Логируем действие
            db.add_moderation_log(
                user_id=target_user.id,
                chat_id=message.chat.id,
                action="manual_warn",
                reason=f"Ручное предупреждение от администратора {message.from_user.username}",
                message_text=""
            )

            self.bot.reply_to(message,
                              f"✅ Пользователю {username} выдано предупреждение!\n"
                              f"📊 Всего предупреждений: {current_warnings + 1}/5",
                              parse_mode='Markdown'
                              )

        except Exception as e:
            logger.error(f"Ошибка при выдаче предупреждения: {e}")
            self.bot.reply_to(message, "❌ Ошибка при выдаче предупреждения!")

    def handle_mute_user(self, message):
        """Обработка команды /mute"""
        # Проверяем права администратора
        try:
            member = self.bot.get_chat_member(message.chat.id, message.from_user.id)
            if member.status not in ['creator', 'administrator']:
                self.bot.reply_to(message, "❌ Эта команда только для администраторов!")
                return
        except:
            self.bot.reply_to(message, "❌ Не удалось проверить права доступа!")
            return

        # Извлекаем параметры из сообщения
        parts = message.text.split(' ', 2)
        if len(parts) < 2:
            self.bot.reply_to(message,
                              "❌ Использование: `/mute @username [время]`\nПример: `/mute @user 1h` или `/mute @user 24h`",
                              parse_mode='Markdown')
            return

        username = parts[1].strip()
        duration = "1h"  # По умолчанию 1 час

        if len(parts) > 2:
            duration = parts[2].strip().lower()

        if not username.startswith('@'):
            self.bot.reply_to(message, "❌ Укажите username в формате @username")
            return

        # Преобразуем время
        try:
            if 'h' in duration:
                hours = int(duration.replace('h', ''))
                mute_duration = hours * 3600
                duration_text = f"{hours} час(ов)"
            elif 'm' in duration:
                minutes = int(duration.replace('m', ''))
                mute_duration = minutes * 60
                duration_text = f"{minutes} минут(ы)"
            else:
                # По умолчанию 1 час
                mute_duration = 3600
                duration_text = "1 час"
        except:
            mute_duration = 3600
            duration_text = "1 час"

        # Получаем ID пользователя по username
        try:
            chat_members = self.bot.get_chat_administrators(message.chat.id)
            target_user = None

            for member in chat_members:
                if member.user.username and member.user.username.lower() == username[1:].lower():
                    target_user = member.user
                    break

            if not target_user:
                self.bot.reply_to(message, f"❌ Пользователь {username} не найден в чате!")
                return

            # Выдаем мут
            until_date = int(time.time()) + mute_duration
            self.bot.restrict_chat_member(
                message.chat.id,
                target_user.id,
                until_date=until_date,
                can_send_messages=False,
                can_send_media_messages=False,
                can_send_other_messages=False
            )

            # Логируем действие
            db.add_moderation_log(
                user_id=target_user.id,
                chat_id=message.chat.id,
                action="manual_mute",
                reason=f"Ручной мут на {duration_text} от администратора {message.from_user.username}",
                message_text=""
            )

            self.bot.reply_to(message,
                              f"✅ Пользователь {username} заглушен на {duration_text}!",
                              parse_mode='Markdown'
                              )

        except Exception as e:
            logger.error(f"Ошибка при выдаче мута: {e}")
            self.bot.reply_to(message, "❌ Ошибка при выдаче мута!")

    def handle_unban_user(self, message):
        """Обработка команды /unban"""
        # Проверяем права администратора
        try:
            member = self.bot.get_chat_member(message.chat.id, message.from_user.id)
            if member.status not in ['creator', 'administrator']:
                self.bot.reply_to(message, "❌ Эта команда только для администраторов!")
                return
        except:
            self.bot.reply_to(message, "❌ Не удалось проверить права доступа!")
            return

        # Извлекаем username из сообщения
        parts = message.text.split(' ', 1)
        if len(parts) < 2:
            self.bot.reply_to(message, "❌ Использование: `/unban @username`", parse_mode='Markdown')
            return

        username = parts[1].strip()
        if not username.startswith('@'):
            self.bot.reply_to(message, "❌ Укажите username в формате @username")
            return

        # Разбаниваем пользователя
        try:
            # Сначала снимаем бан
            self.bot.unban_chat_member(message.chat.id, username[1:])

            # Сбрасываем предупреждения
            cursor = db.conn.cursor()
            cursor.execute('SELECT user_id FROM users WHERE username = ?', (username[1:],))
            user_result = cursor.fetchone()

            if user_result:
                db.update_warnings(user_result[0], 0)

            # Логируем действие
            db.add_moderation_log(
                user_id=user_result[0] if user_result else 0,
                chat_id=message.chat.id,
                action="unban",
                reason=f"Разбан от администратора {message.from_user.username}",
                message_text=""
            )

            self.bot.reply_to(message,
                              f"✅ Пользователь {username} разбанен!\n"
                              f"📊 Счетчик предупреждений сброшен.",
                              parse_mode='Markdown'
                              )

        except Exception as e:
            logger.error(f"Ошибка при разбане: {e}")
            self.bot.reply_to(message, "❌ Ошибка при разбане пользователя!")

    def process_message(self, message):
        """Обработка всех сообщений"""
        # Игнорируем команды
        if message.text.startswith('/'):
            return

        # Проверяем сообщение
        has_violation, bad_word, violation_type = word_filter.check_message(message.text)

        if has_violation:
            self.handle_violation(message, bad_word, violation_type)

        # Обновляем время последней активности
        db.add_user(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.last_name
        )

    def handle_violation(self, message, bad_word, violation_type):
        """Обработка нарушения"""
        user = message.from_user
        chat_id = message.chat.id

        try:
            # Удаляем сообщение
            self.bot.delete_message(chat_id, message.message_id)

            # Получаем текущие предупреждения
            user_data = db.get_user(user.id)
            current_warnings = user_data[4] if user_data else 0
            new_warnings = current_warnings + 1

            # Обновляем предупреждения в БД
            db.update_warnings(user.id, new_warnings)

            # Логируем действие
            db.add_moderation_log(
                user_id=user.id,
                chat_id=chat_id,
                action="message_deleted",
                reason=f"Запрещенное слово: {bad_word} ({violation_type})",
                message_text=message.text[:100]
            )

            # Определяем наказание
            punishment = self.get_punishment(new_warnings)

            # Применяем наказание
            self.apply_punishment(chat_id, user.id, new_warnings, punishment)

            # Отправляем уведомление
            warning_msg = self.create_warning_message(
                user, new_warnings, bad_word, violation_type, punishment
            )

            self.bot.send_message(
                chat_id,
                warning_msg,
                parse_mode='Markdown',
                reply_markup=get_moderation_keyboard(user.id)
            )

            logger.info(f"Удалено сообщение от {user.username}: {message.text[:50]}...")

        except Exception as e:
            logger.error(f"Ошибка при обработке нарушения: {e}")

    def get_punishment(self, warnings_count):
        """Определить наказание по количеству предупреждений"""
        if warnings_count >= 5:
            return {"type": "ban", "duration": None}
        elif warnings_count == 4:
            return {"type": "mute", "duration": 86400}  # 24 часа
        elif warnings_count == 3:
            return {"type": "mute", "duration": 3600}  # 1 час
        else:
            return {"type": "warning", "duration": None}

    def apply_punishment(self, chat_id, user_id, warnings, punishment):
        """Применить наказание"""
        try:
            if punishment["type"] == "mute" and punishment["duration"]:
                until_date = int(time.time()) + punishment["duration"]
                self.bot.restrict_chat_member(
                    chat_id,
                    user_id,
                    until_date=until_date,
                    can_send_messages=False,
                    can_send_media_messages=False,
                    can_send_other_messages=False
                )
            elif punishment["type"] == "ban":
                self.bot.ban_chat_member(chat_id, user_id)
        except Exception as e:
            logger.error(f"Ошибка применения наказания: {e}")

    def create_warning_message(self, user, warnings, bad_word, violation_type, punishment):
        """Создать сообщение о нарушении"""
        username = f"@{user.username}" if user.username else user.first_name

        punishment_text = ""
        if punishment["type"] == "mute":
            hours = punishment["duration"] // 3600
            punishment_text = f"\n🔇 **Наказание:** мут на {hours} часов"
        elif punishment["type"] == "ban":
            punishment_text = "\n⛔ **Наказание:** бан"

        return f"""
⚠️ **Нарушение правил**

👤 **Пользователь:** {username}
📝 **Нарушение:** запрещенное слово
🔍 **Слово:** ||{bad_word}||
📊 **Предупреждений:** {warnings}/5
{punishment_text}

💡 *Сообщение удалено автоматически*
        """

    def welcome_new_member(self, message):
        """Приветствие нового участника"""
        for member in message.new_chat_members:
            if member.id == self.bot.get_me().id:
                # Бот добавлен в чат
                welcome_bot = """
🤖 **Бот-модератор активирован!**

✅ Автоматическая модерация включена
✅ Фильтрация мата активна
✅ Система предупреждений работает

Используйте /help для списка команд
                """
                self.bot.send_message(
                    message.chat.id,
                    welcome_bot,
                    parse_mode='Markdown'
                )
            else:
                welcome_user = f"""
👋 Добро пожаловать, {member.first_name}!

📋 Пожалуйста, ознакомьтесь с правилами:
• Используйте /rules для просмотра правил
• Избегайте нецензурной лексики
• Уважайте других участников

⚠️ Автомодерация активна 24/7
                """
                self.bot.send_message(
                    message.chat.id,
                    welcome_user,
                    parse_mode='Markdown'
                )

    def process_callback(self, call):
        """Обработка callback-запросов"""
        self.bot.answer_callback_query(call.id)

        if call.data.startswith("admin_"):
            self.handle_admin_callback(call)
        elif call.data.startswith("warn_"):
            user_id = int(call.data.split("_")[1])
            self.handle_warn_callback(call, user_id)
        elif call.data.startswith("mute_"):
            parts = call.data.split("_")
            duration = parts[1]
            user_id = int(parts[2])
            self.handle_mute_callback(call, user_id, duration)
        elif call.data.startswith("ban_"):
            user_id = int(call.data.split("_")[1])
            self.handle_ban_callback(call, user_id)
        elif call.data.startswith("forgive_"):
            user_id = int(call.data.split("_")[1])
            self.handle_forgive_callback(call, user_id)
        elif call.data.startswith("details_"):
            user_id = int(call.data.split("_")[1])
            self.handle_details_callback(call, user_id)

    def handle_admin_callback(self, call):
        """Обработка callback от админ-панели"""
        action = call.data.replace("admin_", "")

        if action == "stats":
            stats = db.get_moderation_stats()
            stats_text = f"""
📈 **Статистика модерации:**

• Всего действий: {stats['total_actions']}
• Уникальных нарушителей: {stats['unique_users']}
• Кастомных слов: {stats['custom_words']}
• Активных фильтров: {len(word_filter.patterns)}

🔄 Последнее обновление: {datetime.now().strftime('%H:%M:%S')}
            """

            self.bot.edit_message_text(
                stats_text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=get_admin_keyboard()
            )

        elif action == "words":
            words_text = f"""
📝 **Управление словами:**

• Базовых слов: {len(word_filter.base_words) - len(db.get_custom_words())}
• Пользовательских слов: {len(db.get_custom_words())}
• Всего паттернов: {len(word_filter.patterns)}

*Используйте команды:*
/addword [слово] - добавить слово
/delword [слово] - удалить слово
            """

            self.bot.edit_message_text(
                words_text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=get_admin_keyboard()
            )

    def handle_ban_callback(self, call, user_id):
        """Обработка бана пользователя"""
        try:
            # Бан пользователя
            self.bot.ban_chat_member(call.message.chat.id, user_id)

            # Сбрасываем предупреждения
            db.update_warnings(user_id, 5)  # Устанавливаем максимальное количество

            # Логируем действие
            db.add_moderation_log(
                user_id=user_id,
                chat_id=call.message.chat.id,
                action="manual_ban",
                reason=f"Ручной бан через callback от администратора",
                message_text=""
            )

            self.bot.answer_callback_query(
                call.id,
                "Пользователь забанен!",
                show_alert=True
            )

            # Обновляем сообщение
            self.bot.edit_message_text(
                f"✅ Пользователь забанен!\nID: {user_id}",
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown'
            )

        except Exception as e:
            logger.error(f"Ошибка при выдаче бана: {e}")
            self.bot.answer_callback_query(
                call.id,
                "Ошибка при выдаче бана!",
                show_alert=True
            )

    def handle_forgive_callback(self, call, user_id):
        """Обработка прощения пользователя"""
        try:
            # Сбрасываем предупреждения
            db.update_warnings(user_id, 0)

            # Снимаем мут, если есть
            try:
                self.bot.restrict_chat_member(
                    call.message.chat.id,
                    user_id,
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True
                )
            except:
                pass

            # Логируем действие
            db.add_moderation_log(
                user_id=user_id,
                chat_id=call.message.chat.id,
                action="forgive",
                reason=f"Сброс предупреждений через callback от администратора",
                message_text=""
            )

            self.bot.answer_callback_query(
                call.id,
                "Предупреждения сброшены!",
                show_alert=True
            )

            # Обновляем сообщение
            self.bot.edit_message_text(
                f"✅ Пользователю прощены все нарушения!\nID: {user_id}",
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown'
            )

        except Exception as e:
            logger.error(f"Ошибка при сбросе предупреждений: {e}")
            self.bot.answer_callback_query(
                call.id,
                "Ошибка при сбросе предупреждений!",
                show_alert=True
            )

    def handle_details_callback(self, call, user_id):
        """Обработка запроса подробной информации"""
        try:
            # Получаем информацию о пользователе
            user_data = db.get_user(user_id)

            if user_data:
                user_id, username, first_name, last_name, warnings, muted_until, is_banned, join_date, last_activity = user_data

                # Форматируем даты
                join_date_str = join_date if isinstance(join_date, str) else join_date.strftime(
                    '%Y-%m-%d %H:%M:%S') if join_date else "Неизвестно"
                last_activity_str = last_activity if isinstance(last_activity, str) else last_activity.strftime(
                    '%Y-%m-%d %H:%M:%S') if last_activity else "Неизвестно"

                details_text = f"""
    📋 **Подробная информация**

    👤 **Пользователь:** {first_name} {last_name or ''}
    🔖 **Username:** @{username if username else 'нет'}
    🆔 **ID:** {user_id}

    📊 **Статистика:**
    • Предупреждений: {warnings}/5
    • Забанен: {'Да' if is_banned else 'Нет'}
    • Дата вступления: {join_date_str}
    • Последняя активность: {last_activity_str}

    💬 Для снятия предупреждений нажмите "Простить"
                """
            else:
                details_text = "❌ Информация о пользователе не найдена!"

            self.bot.answer_callback_query(
                call.id,
                "Загружаем информацию...",
                show_alert=False
            )

            # Отправляем новое сообщение с подробностями
            self.bot.send_message(
                call.message.chat.id,
                details_text,
                parse_mode='Markdown'
            )

        except Exception as e:
            logger.error(f"Ошибка при получении деталей: {e}")
            self.bot.answer_callback_query(
                call.id,
                "Ошибка при получении информации!",
                show_alert=True
            )

    def handle_warn_callback(self, call, user_id):
        """Обработка выдачи предупреждения"""
        user_data = db.get_user(user_id)
        if user_data:
            current_warnings = user_data[4]
            db.update_warnings(user_id, current_warnings + 1)

            self.bot.answer_callback_query(
                call.id,
                f"Пользователю выдано предупреждение! Всего: {current_warnings + 1}",
                show_alert=True
            )

    def handle_mute_callback(self, call, user_id, duration):
        """Обработка выдачи мута"""
        try:
            if duration == "1h":
                mute_duration = 3600
                duration_text = "1 час"
            else:  # 24h
                mute_duration = 86400
                duration_text = "24 часа"

            until_date = int(time.time()) + mute_duration
            self.bot.restrict_chat_member(
                call.message.chat.id,
                user_id,
                until_date=until_date,
                can_send_messages=False
            )

            self.bot.answer_callback_query(
                call.id,
                f"Пользователь заглушен на {duration_text}!",
                show_alert=True
            )

        except Exception as e:
            logger.error(f"Ошибка при выдаче мута: {e}")
            self.bot.answer_callback_query(
                call.id,
                "Ошибка при выдаче мута!",
                show_alert=True
            )

    def handle_report(self, message):
        """Обработка жалобы"""
        if message.reply_to_message:
            reported_user = message.reply_to_message.from_user
            reason = message.text.replace('/report', '').strip()

            if not reason:
                reason = "Причина не указана"

            # Отправляем жалобу администраторам
            report_text = f"""
🚨 **Новая жалоба**

👤 **На кого:** @{reported_user.username if reported_user.username else reported_user.first_name}
👤 **Кто жаловался:** @{message.from_user.username if message.from_user.username else message.from_user.first_name}
📝 **Причина:** {reason}
🕐 **Время:** {datetime.now().strftime('%H:%M:%S')}

💬 **Сообщение:** {message.reply_to_message.text[:200]}
            """

            # Ищем администраторов
            admins = self.bot.get_chat_administrators(message.chat.id)
            for admin in admins:
                if not admin.user.is_bot:
                    try:
                        self.bot.send_message(
                            admin.user.id,
                            report_text,
                            parse_mode='Markdown'
                        )
                    except:
                        pass

            self.bot.reply_to(
                message,
                "✅ Ваша жалоба отправлена администраторам!",
                parse_mode='Markdown'
            )
        else:
            self.bot.reply_to(
                message,
                "❌ Пожалуйста, используйте эту команду как ответ на сообщение, на которое хотите пожаловаться.",
                parse_mode='Markdown'
            )