import schedule
import time
from threading import Thread

from main import run_bot, nearest_date

from constants import MESSAGE_TIME, OUR_TIMEZONE


schedule.every().day.at(MESSAGE_TIME, OUR_TIMEZONE).do(
    lambda: nearest_date(for_group=True)
)


def start_timer():
    """Запуск расписания для вывода сообщения в указанное время."""
    while True:
        schedule.run_pending()  # ожидание выполнения
        time.sleep(1)


if __name__ == '__main__':
    # Запуск расписания в отдельном потоке
    scheduler_thread = Thread(target=start_timer)
    scheduler_thread.start()

    # Запуск бота, с которым можно взаимодействовать:
    run_bot()
