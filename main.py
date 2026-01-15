import logging
import os
import sys
from pathlib import Path

# Добавляем src в путь для импортов
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from telebot import TeleBot
from config import Config
from database import db
from handlers import MessageHandler

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def create_directories():
    """Создать необходимые директории"""
    directories = ['data', 'data/logs']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Создана директория: {directory}")


def main():
    """Основная функция запуска бота"""

    # Создаем директории
    create_directories()

    # Проверяем токен
    if not Config.TOKEN:
        logger.error("Токен бота не найден! Укажите его в .env файле")
        return

    # Создаем экземпляр бота
    bot = TeleBot(Config.TOKEN, parse_mode='HTML')

    # Инициализируем обработчики
    handler = MessageHandler(bot)

    logger.info("=" * 60)
    logger.info("🤖 Умный бот-модератор запускается...")
    logger.info(f"⚙️  База данных: {Config.DB_PATH}")
    logger.info("=" * 60)

    try:
        # Запускаем бота
        logger.info("✅ Бот успешно запущен!")
        bot.polling(none_stop=True, interval=0)

    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")
        raise

    finally:
        # Закрываем соединение с БД
        db.close()
        logger.info("📴 Бот остановлен")


if __name__ == '__main__':
    main()