import sqlite3
import logging
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        self.conn = None
        self.init_db()

    def init_db(self):
        """Инициализация базы данных"""
        try:
            self.conn = sqlite3.connect(Config.DB_PATH, check_same_thread=False)
            cursor = self.conn.cursor()

            # Таблица пользователей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    warnings INTEGER DEFAULT 0,
                    muted_until INTEGER DEFAULT 0,
                    is_banned BOOLEAN DEFAULT FALSE,
                    join_date TIMESTAMP,
                    last_activity TIMESTAMP
                )
            ''')

            # Таблица логов модерации
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS moderation_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    chat_id INTEGER,
                    action TEXT,
                    reason TEXT,
                    message_text TEXT,
                    timestamp TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')

            # Таблица кастомных слов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS custom_words (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT UNIQUE,
                    added_by INTEGER,
                    added_at TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')

            self.conn.commit()
            logger.info("База данных инициализирована")

        except Exception as e:
            logger.error(f"Ошибка инициализации БД: {e}")

    def get_user(self, user_id):
        """Получить информацию о пользователе"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM users WHERE user_id = ?
        ''', (user_id,))
        return cursor.fetchone()

    def get_user_by_username(self, username):
        """Получить информацию о пользователе по username"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM users WHERE username = ?
        ''', (username,))
        return cursor.fetchone()

    def add_user(self, user_id, username, first_name, last_name):
        """Добавить нового пользователя"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO users 
            (user_id, username, first_name, last_name, join_date, last_activity)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name,
              datetime.now(), datetime.now()))
        self.conn.commit()

    def update_warnings(self, user_id, warnings):
        """Обновить количество предупреждений"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE users 
            SET warnings = ?, last_activity = ?
            WHERE user_id = ?
        ''', (warnings, datetime.now(), user_id))
        self.conn.commit()

    def add_moderation_log(self, user_id, chat_id, action, reason, message_text):
        """Добавить запись в лог модерации"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO moderation_logs 
            (user_id, chat_id, action, reason, message_text, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, chat_id, action, reason, message_text, datetime.now()))
        self.conn.commit()

    def get_moderation_stats(self):
        """Получить статистику модерации"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM moderation_logs')
        total_actions = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(DISTINCT user_id) FROM moderation_logs')
        unique_users = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM custom_words WHERE is_active = 1')
        custom_words = cursor.fetchone()[0]

        return {
            'total_actions': total_actions,
            'unique_users': unique_users,
            'custom_words': custom_words
        }

    def add_custom_word(self, word, added_by):
        """Добавить кастомное запрещенное слово"""
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO custom_words (word, added_by, added_at)
                VALUES (?, ?, ?)
            ''', (word, added_by, datetime.now()))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_custom_words(self):
        """Получить все кастомные слова"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT word FROM custom_words WHERE is_active = 1')
        return [row[0] for row in cursor.fetchall()]

    def close(self):
        """Закрыть соединение с БД"""
        if self.conn:
            self.conn.close()


# Глобальный экземпляр БД
db = Database()