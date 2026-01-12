import re
import json
import logging
from typing import List, Tuple
from config import Config
from database import db

logger = logging.getLogger(__name__)


class WordFilter:
    def __init__(self):
        self.base_words = []
        self.patterns = []
        self.load_words()

    def load_words(self):
        """Загрузить запрещенные слова из файла и БД"""
        try:
            # Загружаем базовые слова из JSON
            with open(Config.BANNED_WORDS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.base_words = data.get('banned_words', [])

            # Добавляем кастомные слова из БД
            custom_words = db.get_custom_words()
            self.base_words.extend(custom_words)

            # Генерируем паттерны
            self.generate_patterns()

            logger.info(f"Загружено {len(self.base_words)} запрещенных слов")

        except FileNotFoundError:
            # Создаем файл с базовыми словами если не существует
            self.create_default_words_file()
            self.load_words()
        except Exception as e:
            logger.error(f"Ошибка загрузки слов: {e}")

    def create_default_words_file(self):
        """Создать файл с базовыми запрещенными словами"""
        default_words = [
            "блять", "блядь", "пизда", "пиздец", "ебать", "ёб", "ебал",
            "хуй", "хуё", "мудак", "гондон", "сука", "дрочить", "трахать",
            "вагина", "член", "хер", "анус", "жопа", "сперма", "секс",
            "шлюха", "проститутка", "пидор", "гомик",
            "нацист", "фашист", "расист", "жид",
            "дебил", "идиот", "дурак", "тупица", "кретин", "даун",
            "лох", "лошара", "чмо", "отстой", "говно", "дерьмо",
            "срать", "срань", "залупа"
        ]

        data = {
            "banned_words": default_words,
            "version": "1.0",
            "description": "База запрещенных слов для бота-модератора"
        }

        with open(Config.BANNED_WORDS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def generate_patterns(self):
        """Сгенерировать паттерны для поиска"""
        self.patterns = []

        for word in self.base_words:
            # Паттерн с учетом замены букв
            pattern_parts = []
            for char in word:
                if char in Config.CHAR_REPLACEMENTS:
                    replacements = Config.CHAR_REPLACEMENTS[char]
                    # Экранируем специальные символы
                    escaped = [re.escape(r) for r in replacements]
                    pattern_parts.append(f'[{"".join(escaped)}]')
                else:
                    pattern_parts.append(re.escape(char))

            # Добавляем возможность разделителей между символами
            pattern = r'[\s\-_\.]*'.join(pattern_parts)

            # Добавляем возможность повторения символов (ппривветт)
            final_pattern = ''
            for part in pattern_parts:
                final_pattern += f'{part}+[\s\-_\.]*'

            self.patterns.append(final_pattern.rstrip(r'[\s\-_\.]*'))

    def check_message(self, text: str) -> Tuple[bool, str, str]:
        """
        Проверить сообщение на наличие запрещенных слов

        Возвращает: (найдено_ли, слово, тип_нарушения)
        """
        text_lower = text.lower()

        # 1. Проверка по паттернам
        for i, pattern in enumerate(self.patterns):
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True, self.base_words[i], "pattern_match"

        # 2. Проверка без пробелов
        text_no_spaces = re.sub(r'[\s\-_\.]', '', text_lower)
        for word in self.base_words:
            if len(word) > 3 and word in text_no_spaces:
                return True, word, "no_spaces"

        # 3. Проверка на транслит
        translit_variants = self.generate_translit_variants(text_lower)
        for variant in translit_variants:
            for word in self.base_words:
                if word in variant:
                    return True, word, "translit"

        # 4. Проверка на разбиение слова (п р и в е т)
        spaced_text = ' '.join(text_lower)
        for word in self.base_words:
            spaced_word = ' '.join(word)
            if spaced_word in spaced_text:
                return True, word, "spaced"

        return False, "", ""

    def generate_translit_variants(self, text: str) -> List[str]:
        """Генерировать варианты текста с заменой русских букв на английские"""
        variants = [text]

        # Простая замена часто используемых букв
        replacements = {
            'a': 'а',
            'b': 'в',
            'c': 'с',
            'e': 'е',
            'k': 'к',
            'm': 'м',
            'o': 'о',
            'p': 'р',
            't': 'т',
            'x': 'х',
            'y': 'у'
        }

        # Меняем английские буквы на русские
        for eng, rus in replacements.items():
            variant = text.replace(eng, rus)
            if variant != text:
                variants.append(variant)

        return variants

    def add_custom_word(self, word: str) -> bool:
        """Добавить новое запрещенное слово"""
        if word not in self.base_words:
            self.base_words.append(word)
            self.generate_patterns()
            return True
        return False


# Глобальный экземпляр фильтра
word_filter = WordFilter()