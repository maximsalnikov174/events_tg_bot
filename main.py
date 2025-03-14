import os
import re
import sqlite3
from datetime import date
from typing import Optional, Union


from dotenv import load_dotenv
from telebot import TeleBot, types
from telebot.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup)

from function import Event
from keyboards import NEAREST_DATE_BUTTON, TEST_BUTTON
from substitutions import get_full_value_declension


load_dotenv()

today = date.today()
today_year = today.year

# Создаём бота:
bot = TeleBot(token=os.getenv('BOT_TOKEN'))
chat_id = os.getenv('TG_GROUP_ID')


def _get_group_or_personal(message) -> Optional[str]:
    """Определяет тип источника запроса и возвращает ID из .env."""
    return os.getenv('TG_THREAD_ID') if message.message_thread_id else None


def _send_message(message, some_text, keyboard=None) -> types.Message:
    """Отправляет сообщение либо в чат группы, либо лично."""
    bot.send_message(
        chat_id=message.chat.id,
        text=some_text,
        reply_markup=keyboard,
        message_thread_id=_get_group_or_personal(message)
    )


def _get_events_stack(
    events,
    events_stack: list = [],
    minimal_days_delta=float('inf')
):
    """Возвращает ближайшее(-ие) событие(-я) и оставшиеся до него(-их) дни."""
    for event in events:
        event_day, event_month = int(event[1][:2]), int(event[1][2:])
        event_in_format = date(today_year, event_month, event_day)
        delta = (event_in_format - today).days

        if delta < 0:
            pass  # значит - уже прошло
        elif delta == minimal_days_delta:
            events_stack.append(event)
        elif delta < minimal_days_delta:
            minimal_days_delta = delta
            events_stack = [event]

    return (minimal_days_delta, events_stack)


@bot.message_handler(commands=['start'])
def wake_up(message):
    """Стартовая функция, запускающая бота с сообщением."""

    # Создаём объект клавиатуры:
    # keyboard = ReplyKeyboardMarkup(
    #     resize_keyboard=True
    # )
    # button_next_event = KeyboardButton('/next')  # Создаем объект кнопки.
    # button_test = KeyboardButton('/test')
    # keyboard.add(button_next_event, button_test)  # Добавляем кнопки на клаву.

    keyboard_buttons = [NEAREST_DATE_BUTTON, TEST_BUTTON]
    keyboard = InlineKeyboardMarkup(keyboard_buttons)
    _send_message(message, 'Привет! Нажми нужную кнопку.', keyboard)


@bot.message_handler(commands=['test'])
def test_me(message):
    _send_message(message, 'Просто тест!')


@bot.message_handler(commands=['next'])
def nearest_date(message):
    """Отправляет сообщение о ближайшем событии в ТГ-бот."""
    try:
        # Подключаемся к базе данных:
        conn = sqlite3.connect('events.db')
        cursor = conn.cursor()
        # Чтение данных из базы и создание переменной со списком строк:
        cursor.execute('SELECT * FROM events')
        rows = cursor.fetchall()

        result = _get_events_stack(rows)  # Получение ближайшего события(-й)

        # Подготовка сообщения о ближайшем событии для вывода результата в ТГ:
        if result:
            minimal_days_delta, events_stack_from_db = result

            # Подбираем окончания к словам «ближайшие» и «события»:
            word_in_message = 'е' if len(events_stack_from_db) == 1 else 'ия'
            time_left = get_full_value_declension(minimal_days_delta, "days")

            events_stack = []
            for event in events_stack_from_db:
                events_stack.append(Event(*event[1:]).as_view())
            events_stack = ', '.join(map(str, events_stack))
            new_message = (
                f'Ближайш{word_in_message[0]}е событи{word_in_message[-1]} '
                f'(через {time_left}):\n{events_stack}'
            )

        _send_message(message, new_message)

        # Закрытие соединения с базой данных:
        conn.close()
    except Exception as e:
        print(e)


# Перечень всех рабочих функций для кнопок:
FUNCTION_FROM_COMMAND = {
    'test_me_command': test_me,
    'nearest_date_command': nearest_date
}


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    """Из списка function_from_command возвращает функцию callback-запроса."""
    function_name = FUNCTION_FROM_COMMAND.get(call.data)
    function_name(call.message)


# Сохранение изменений в базе данных:
# conn.commit()

if __name__ == '__main__':
    bot.polling(none_stop=True, interval=5)
