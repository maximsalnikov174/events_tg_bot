import os
import sqlite3
from datetime import date
import time
# from typing import Optional, Union

from dotenv import load_dotenv
from telebot import TeleBot, types
from telebot.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup)

from constants import (BOT_POOLING_TIMEOUT, BOT_POOLING_INTERVAL,
                       RELOAD_BOT_TIMER)
from function import Event
from keyboards import (FUNCTION_FROM_COMMAND, NEAREST_DATE_BUTTON, TEST_BUTTON)
from substitutions import (get_full_value_declension,
                           get_full_values_with_declension)

load_dotenv()

today = date.today()
today_year = today.year

# Создаём бота:
bot = TeleBot(token=os.getenv('BOT_TOKEN'))


def _send_message(
    some_text, message=None, keyboard=None, **kwargs
) -> types.Message:
    """Отправляет сообщение в тред нашей группы или лично."""
    # для нашей группы (если в _send_message есть kwargs «for_group»):
    if 'for_group' in kwargs and kwargs['for_group']:
        chat_id = os.getenv('TG_GROUP_ID')  # id группы семейки
        thread_id = os.getenv('TG_THREAD_ID')  # id треда объявлений

    # для личного чата (получаем только chat.id):
    else:
        chat_id = message.chat.id  # id чата из тела message
        thread_id = None

    # Отправка сообщения:
    bot.send_message(
        chat_id=chat_id,
        text=some_text,
        reply_markup=keyboard,
        message_thread_id=thread_id
    )


def _get_events_from_stack(
    events,
    events_stack: list = [],
    minimal_days_delta=float('inf')
) -> tuple[int, list]:
    """Возвращает ближайшее(-ие) событие(-я) и оставшиеся до него(-их) дни.

    На вход подаются строки событий из БД, после чего перебором собирается
    список событий, выпадающих на ближайшую (относительно сегодня) дату
    и количество дней до этих событий."""
    for event in events:
        event_day, event_month = int(event[1][:2]), int(event[1][2:])
        event_in_format = date(today_year, event_month, event_day)
        delta = (event_in_format - today).days

        if delta < 0:  # событие уже прошло
            pass
        elif delta == minimal_days_delta:  # несколько событий в один день
            events_stack.append(event)
        elif delta < minimal_days_delta:  # найден более близкий день
            minimal_days_delta = delta
            events_stack = [event]

    return (minimal_days_delta, events_stack)


def _generates_text_for_the_nearest_date():
    """Готовит сообщение о ближайшем событии."""
    # FIXME: не понятно, как работает «', '.join(map(str, events_stack))»

    try:
        # Подключаемся к базе данных:
        conn = sqlite3.connect('events.db')
        cursor = conn.cursor()
        # Чтение данных из базы и создание переменной со списком строк:
        cursor.execute('SELECT * FROM events')
        rows = cursor.fetchall()

        # Закрытие соединения с базой данных:
        conn.close()

        result = _get_events_from_stack(rows)  # Получение ближайших событий.

        # Подготовка данных о ближайших событиях для вывода результата в ТГ:
        # if result:
        minimal_days_delta, events_stack_from_db = result

        events_stack = []
        for event in events_stack_from_db:
            events_stack.append(Event(*event[1:]).as_view())
        events_stack = ', '.join(map(str, events_stack))

        # Формирование сообщения с учётом оставшихся дней:
        days_left = ['Сегодня', 'Уже завтра']
        if minimal_days_delta <= 1:
            new_message = (
                f'{days_left[minimal_days_delta]}:\n{events_stack}'
            )
        else:
            # Подбираем окончания к словам «ближайшИе» и «событиЯ»:
            time_left = get_full_value_declension(
                minimal_days_delta, "days"
            )
            word_in_message = (
                'е' if len(events_stack_from_db) == 1 else 'ия'
            )
            new_message = (
                f'Ближайш{word_in_message[0]}е событи{word_in_message[-1]}'
                f' (через {time_left}):\n{events_stack}'
            )
    except Exception as e:
        print(e)

    return new_message


# Сохранение изменений в базе данных
# пригодится при записи/перезаписи:
# conn.commit()


# СТАРТОВАЯ ФУНКЦИЯ ДЛЯ ОБЩЕНИЯ С БОТОМ:
# --------------------------------------
@bot.message_handler(commands=['start'])
def wake_up(message):
    """Стартовая функция, запускающая бота с сообщением."""

    # Создаём объект клавиатуры:
    # keyboard = ReplyKeyboardMarkup(
    #     resize_keyboard=True
    # )
    # button_next_event = KeyboardButton('/next')  # Создаем объект кнопки.
    # button_test = KeyboardButton('/test')
    # keyboard.add(button_next_event, button_test)  # Добавляем кнопки на клаву

    keyboard_buttons = [NEAREST_DATE_BUTTON, TEST_BUTTON]
    keyboard = InlineKeyboardMarkup(keyboard_buttons)
    _send_message(
        some_text='Привет! Нажми нужную кнопку.',
        message=message,
        keyboard=keyboard,
        for_group=bool(message.message_thread_id)
    )


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    """Из списка FUNCTION_FROM_COMMAND возвращает функцию callback-запроса."""
    function_name = FUNCTION_FROM_COMMAND.get(call.data)
    if function_name:
        function_name(call.message)
    else:
        print(f"Неизвестный callback: {call.data}")


def run_tg_bot():
    """Запускает бота и перезапускает, если выскакивает исключение."""
    try:
        bot.polling(
            none_stop=True,
            interval=BOT_POOLING_INTERVAL,
            timeout=BOT_POOLING_TIMEOUT
        )
    except Exception as e:
        print(
            f'Ошибка {e}.'
            f'{get_full_values_with_declension(RELOAD_BOT_TIMER)}'
        )
        time.sleep(RELOAD_BOT_TIMER)
        # FIXME проверить, перезапускается ли функция


# ВЗАИМОДЕЙСТВИЕ С БОТОМ ЧЕРЕЗ КЛАВИАТУРЫ:

# функция 1
@bot.message_handler(commands=['test'])
def test_me(message):
    """Тестовая функция."""
    _send_message(
        'Просто тест!',
        message=message,
        for_group=bool(message.message_thread_id)
    )


# функция 2
@bot.message_handler(commands=['next'])
def send_response(message):
    """В ответ на запрос отправляет сообщение о ближайшем событии в ТГ-бот."""
    _send_message(
        _generates_text_for_the_nearest_date(),
        message=message,
        for_group=bool(message.message_thread_id)
    )


# АВТОМАТИЧЕСКАЯ ОТПРАВКА СООБЩЕНИЙ В ГРУППУ:
def nearest_date(for_group=True, **kwargs):
    """По расписанию отправляет сообщение о ближайшем событии в ТГ-бот."""
    _send_message(
        _generates_text_for_the_nearest_date(),
        for_group=for_group
    )
