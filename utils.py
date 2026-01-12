import telebot
import re

# Замени 'TOKEN' на токен от @BotFather
TOKEN = 'BOT_TOKEN'
bot = telebot.TeleBot(TOKEN)

# Словарь замен для обхода фильтра (буквы -> возможные замены)
CHAR_REPLACEMENTS = {
    'а': ['а', 'a', '@'],
    'б': ['б', 'b', '6'],
    'в': ['в', 'v', 'b'],
    'г': ['г', 'g', 'r'],
    'д': ['д', 'd'],
    'е': ['е', 'e'],
    'ё': ['ё', 'е', 'e'],
    'ж': ['ж', 'zh', 'z*'],
    'з': ['з', 'z', '3'],
    'и': ['и', 'i', 'u'],
    'й': ['й', 'j', 'y', 'i'],
    'к': ['к', 'k'],
    'л': ['л', 'l'],
    'м': ['м', 'm'],
    'н': ['н', 'n'],
    'о': ['о', 'o', '0'],
    'п': ['п', 'p', 'n', 'п'],
    'р': ['р', 'r', 'p'],
    'с': ['с', 'c', 's'],
    'т': ['т', 't', 'm'],
    'у': ['у', 'y', 'u'],
    'ф': ['ф', 'f'],
    'х': ['х', 'x', 'h'],
    'ц': ['ц', 'c', 'ts'],
    'ч': ['ч', 'ch', '4'],
    'ш': ['ш', 'sh'],
    'щ': ['щ', 'sch', 'shch'],
    'ъ': ['ъ', ''],
    'ы': ['ы', 'i', 'y'],
    'ь': ['ь', ''],
    'э': ['э', 'e', 'э'],
    'ю': ['ю', 'yu', 'iu'],
    'я': ['я', 'ya', 'ia']
}

# Базовые запрещенные слова (в нормальной форме)
BASE_BAD_WORDS = [
    'блять', 'блядь', 'пизда', 'пиздец', 'ебать', 'ёб', 'ебал',
    'хуй', 'хуё', 'мудак', 'гондон', 'сука', 'дрочить', 'трахать',
    'вагина', 'член', 'хер', 'анус', 'жопа', 'сперма', 'секс',
    'шлюха', 'проститутка', 'педераст', 'пидор', 'гомик',
    'нацист', 'фашист', 'расист', 'жид', 'черножопый',
    'дебил', 'идиот', 'дурак', 'тупица', 'кретин', 'даун',
    'лох', 'лошара', 'чмо', 'отстой', 'говно', 'дерьмо',
    'срать', 'срань', 'залупа', 'залупой', 'залупиться'
]


# Создаем расширенный список слов с разными вариантами написания
def generate_word_variants(word):
    variants = set()
    # Добавляем базовое слово
    variants.add(word)

    # Добавляем варианты с заменой русских букв на английские
    for rus_char, eng_chars in CHAR_REPLACEMENTS.items():
        if rus_char in word:
            for eng_char in eng_chars:
                variant = word.replace(rus_char, eng_char)
                variants.add(variant)

    # Добавляем варианты с разными комбинациями замен
    for i in range(len(word)):
        if word[i] in CHAR_REPLACEMENTS:
            for replacement in CHAR_REPLACEMENTS[word[i]]:
                variant = word[:i] + replacement + word[i + 1:]
                variants.add(variant)

    return list(variants)


# Генерируем полный список запрещенных слов
BAD_WORDS = []
for base_word in BASE_BAD_WORDS:
    BAD_WORDS.extend(generate_word_variants(base_word))

# Также добавляем слова с разделителями и повторениями
EXTENDED_BAD_PATTERNS = []
for base_word in BASE_BAD_WORDS:
    # Паттерн для слов с разделителями (м-а-т, м.а.т, м а т)
    pattern = ''
    for char in base_word:
        if char in CHAR_REPLACEMENTS:
            possible_chars = CHAR_REPLACEMENTS[char]
            pattern += f'[{"".join(possible_chars)}]'
        else:
            pattern += char
        pattern += r'[\s\-_\.]*'

    EXTENDED_BAD_PATTERNS.append(pattern[:-len(r'[\s\-_\.]*')])


# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = """
Привет! Я умный бот-модератор.

🔒 **Особенности фильтрации:**
• Распознаю мат с заменой букв (рус/англ)
• Ловлю скрытые слова с разделителями
• Удаляю сообщения с нарушением правил

📋 **Доступные команды:**
/help - помощь
/rules - правила
/stats - статистика
/addword - добавить слово (админы)
    """
    bot.send_message(message.chat.id, welcome_text, parse_mode='Markdown')


# Команда /help
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
🤖 **Команды бота:**

**Для всех:**
/start - начать работу
/help - эта справка
/rules - правила чата
/stats - статистика работы

**Для администраторов:**
/addword [слово] - добавить слово в фильтр
/listwords - показать список запрещенных слов
/delword [слово] - удалить слово из фильтра
/warn [@username] - выдать предупреждение
/unwarn [@username] - снять предупреждение

**Для разработчика:**
/debug - отладочная информация
    """
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')


# Команда /rules
@bot.message_handler(commands=['rules'])
def send_rules(message):
    rules_text = """
📜 **Правила чата:**

1. ❌ **Запрещено:**
   - Нецензурная лексика (мат, оскорбления)
   - Оскорбления по расовому, национальному или религиозному признаку
   - Угрозы и запугивания
   - Порнографический контент

2. ✅ **Разрешено:**
   - Конструктивное общение
   - Вежливое обсуждение
   - Помощь друг другу

3. ⚠️ **Наказания:**
   - 1 нарушение: удаление сообщения + предупреждение
   - 3 предупреждения: мут на 1 час
   - 5 предупреждений: бан на сутки
   - Систематические нарушения: перманентный бан
    """
    bot.send_message(message.chat.id, rules_text, parse_mode='Markdown')


# Команда /stats
@bot.message_handler(commands=['stats'])
def send_stats(message):
    stats_text = f"""
📊 **Статистика бота:**

• Загружено {len(BASE_BAD_WORDS)} базовых запрещенных слов
• Сгенерировано {len(BAD_WORDS)} вариантов написания
• Загружено {len(EXTENDED_BAD_PATTERNS)} паттернов для поиска
• Активные фильтры: проверка замен букв, разделителей, регистра
    """
    bot.send_message(message.chat.id, stats_text, parse_mode='Markdown')


# Хранилище для предупреждений (в реальном проекте используйте БД)
warnings_storage = {}


# Улучшенная функция проверки текста
def check_text_for_bad_words(text):
    text_lower = text.lower()

    # 1. Проверка по точному совпадению в BAD_WORDS
    for word in BAD_WORDS:
        if word in text_lower:
            return True, f"Запрещенное слово: {word}"

    # 2. Проверка по паттернам (с разделителями)
    for pattern in EXTENDED_BAD_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return True, f"Обнаружен запрещенный паттерн"

    # 3. Проверка на обход фильтра через пробелы/разделители
    text_without_spaces = re.sub(r'[\s\-_\.]', '', text_lower)
    for word in BAD_WORDS:
        if len(word) > 3 and word in text_without_spaces:
            return True, f"Запрещенное слово с разделителями"

    # 4. Проверка на повторяющиеся символы (типа "приввеет")
    for base_word in BASE_BAD_WORDS:
        if len(base_word) > 3:
            # Создаем паттерн с возможными повторениями символов
            pattern = ''
            for char in base_word:
                pattern += f'{re.escape(char)}+'

            if re.search(pattern, text_lower, re.IGNORECASE):
                # Проверяем, что найденная последовательность похожа на запрещенное слово
                match = re.search(pattern, text_lower, re.IGNORECASE)
                if match:
                    matched_text = match.group()
                    # Если длина найденного текста близка к длине базового слова
                    if abs(len(matched_text) - len(base_word)) <= 3:
                        return True, f"Запрещенное слово с повторениями символов"

    return False, None


# Команда для добавления слов (админам)
@bot.message_handler(commands=['addword'])
def add_bad_word(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    try:
        member = bot.get_chat_member(chat_id, user_id)
        if member.status in ['creator', 'administrator']:
            words = message.text.split()[1:]
            if words:
                added_words = []
                for word in words:
                    if word.lower() not in BASE_BAD_WORDS:
                        BASE_BAD_WORDS.append(word.lower())
                        # Обновляем BAD_WORDS
                        BAD_WORDS.extend(generate_word_variants(word.lower()))
                        added_words.append(word.lower())

                bot.reply_to(message, f"✅ Добавлено {len(added_words)} слов: {', '.join(added_words)}")
            else:
                bot.reply_to(message, "Использование: /addword слово1 слово2 ...")
        else:
            bot.reply_to(message, "❌ Эта команда только для администраторов!")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")


# Команда для просмотра запрещенных слов (админам)
@bot.message_handler(commands=['listwords'])
def list_bad_words(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    try:
        member = bot.get_chat_member(chat_id, user_id)
        if member.status in ['creator', 'administrator']:
            words_list = "\n".join(BASE_BAD_WORDS[:50])  # Показываем первые 50 слов
            if len(BASE_BAD_WORDS) > 50:
                words_list += f"\n\n... и ещё {len(BASE_BAD_WORDS) - 50} слов"
            bot.reply_to(message, f"📝 Список запрещенных слов:\n{words_list}")
        else:
            bot.reply_to(message, "❌ Эта команда только для администраторов!")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")


# Обработчик всех текстовых сообщений
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_all_messages(message):
    text = message.text

    # Проверяем текст
    has_bad_content, reason = check_text_for_bad_words(text)

    if has_bad_content:
        try:
            # Удаляем сообщение
            bot.delete_message(message.chat.id, message.message_id)

            # Увеличиваем счетчик предупреждений
            user_id = message.from_user.id
            if user_id not in warnings_storage:
                warnings_storage[user_id] = 0
            warnings_storage[user_id] += 1

            warnings_count = warnings_storage[user_id]
            username = message.from_user.username if message.from_user.username else message.from_user.first_name

            # Формируем сообщение в зависимости от количества предупреждений
            if warnings_count == 1:
                action = "⚠️ Первое предупреждение"
                duration = ""
            elif warnings_count == 2:
                action = "⚠️ Второе предупреждение"
                duration = ""
            elif warnings_count == 3:
                action = "🔇 Мут на 1 час"
                try:
                    # Устанавливаем ограничения на отправку сообщений
                    until_date = int(time.time()) + 3600
                    bot.restrict_chat_member(
                        message.chat.id,
                        user_id,
                        until_date=until_date,
                        can_send_messages=False
                    )
                except:
                    pass
                duration = "⏰ Срок: 1 час"
            elif warnings_count >= 5:
                action = "⛔ Бан"
                try:
                    bot.ban_chat_member(message.chat.id, user_id)
                    del warnings_storage[user_id]
                except:
                    pass
                duration = ""
            else:
                action = "⚠️ Предупреждение"
                duration = ""

            # Отправляем уведомление
            warning_msg = f"""
{action} для @{username}

📝 **Причина:** {reason}
📊 **Предупреждений:** {warnings_count}/5
{duration}

💡 Пожалуйста, соблюдайте правила чата.
            """

            bot.send_message(message.chat.id, warning_msg, parse_mode='Markdown')

            # Логируем в консоль
            print(f"[МОДЕРАЦИЯ] Удалено сообщение от {username}: {text[:50]}...")
            print(f"[МОДЕРАЦИЯ] Причина: {reason}")
            print(f"[МОДЕРАЦИЯ] Предупреждений: {warnings_count}")

        except Exception as e:
            print(f"[ОШИБКА] Не удалось удалить сообщение: {e}")
            bot.reply_to(message, "⚠️ Обнаружено запрещенное содержание!")


# Обработчик новых участников
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    for member in message.new_chat_members:
        if member.id == bot.get_me().id:
            # Бот добавлен в чат
            bot.send_message(message.chat.id,
                             "🤖 Спасибо за добавление! Я готов к работе.\n\nИспользуйте /help для списка команд.")
        else:
            welcome_msg = f"""
👋 Добро пожаловать, {member.first_name}!

📋 **Обязательно ознакомьтесь с правилами:**
• Используйте /rules для просмотра правил
• Используйте /help для списка команд

⚠️ **Внимание:** сообщения с нарушением правил будут удаляться автоматически.
            """
            bot.send_message(message.chat.id, welcome_msg, parse_mode='Markdown')


# Запуск бота
if __name__ == '__main__':
    import time

    print("=" * 50)
    print("🤖 Умный бот-модератор запущен!")
    print(f"📊 Базовых слов: {len(BASE_BAD_WORDS)}")
    print(f"📊 Всего вариантов: {len(BAD_WORDS)}")
    print(f"📊 Паттернов: {len(EXTENDED_BAD_PATTERNS)}")
    print("=" * 50)
    print("⚙️  Возможности фильтрации:")
    print("• Замена русских букв на английские")
    print("• Слова с разделителями (пробелы, точки, тире)")
    print("• Повторяющиеся символы")
    print("• Разный регистр")
    print("=" * 50)

    bot.polling(none_stop=True)