from telebot.types import InlineKeyboardButton

from main import test_me, send_response


NEAREST_DATE_BUTTON = [
    InlineKeyboardButton(
        'Ближайшее событие',
        callback_data='nearest_date_command'
    )
]

TEST_BUTTON = [
    InlineKeyboardButton(
        'Тест',
        callback_data='test_me_command'
    )
]

# Перечень всех рабочих функций, связанных с кнопками:
FUNCTION_FROM_COMMAND = {
    'test_me_command': test_me,
    'nearest_date_command': send_response
}
