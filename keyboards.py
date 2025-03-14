from telebot.types import InlineKeyboardButton


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
