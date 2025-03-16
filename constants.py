from pathlib import Path
from typing import Final


MDAYS = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

MONTH_NAME = [
    '', 'январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль',
    'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь'
]

DAY_NAME = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']

MIN_YEAR = 1900

MAX_YEAR = 2050

BASE_DIR = Path(__file__)

# Константы для логгирования:
LOG_DIR = BASE_DIR / 'logs'
LOG_FILE = LOG_DIR / 'tg_bot.log'
MAX_BYTES_FOR_LOG_FILE = 10 ** 6
BACKUP_COUNT = 5
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'

# Отправка сообщений по расписанию
MESSAGE_TIME = '09:00'
OUR_TIMEZONE = 'Asia/Yekaterinburg'

# Запуск бота через pooling:
RELOAD_BOT_TIMER: Final[int] = 60
BOT_POOLING_TIMEOUT: Final[int] = 50
BOT_POOLING_INTERVAL: Final[int] = 5
