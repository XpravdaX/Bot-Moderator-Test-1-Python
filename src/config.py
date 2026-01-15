import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv(Path(__file__).parent.parent / '.env')


class Config:
    # Токен бота из переменных окружения
    TOKEN = os.getenv('BOT_TOKEN')

    # Настройки базы данных
    DB_PATH = Path(__file__).parent.parent / 'data' / 'users_data.db'

    # Настройки модерации
    MAX_WARNINGS = 5
    MUTE_DURATIONS = {
        1: 0,  # Первое предупреждение - без мута
        2: 0,  # Второе - без мута
        3: 3600,  # Третье - мут на 1 час
        4: 7200,  # Четвертое - мут на 2 часа
        5: 86400  # Пятое - бан на сутки
    }

    # Пути к файлам
    BANNED_WORDS_FILE = Path(__file__).parent.parent / 'data' / 'banned_words.json'
    LOGS_DIR = Path(__file__).parent.parent / 'data' / 'logs'

    # Настройки логирования
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Символы для замены (обход фильтра)
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
        'п': ['п', 'p', 'n'],
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
        'э': ['э', 'e'],
        'ю': ['ю', 'yu', 'iu'],
        'я': ['я', 'ya', 'ia']
    }