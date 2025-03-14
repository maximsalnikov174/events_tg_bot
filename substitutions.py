import regex

from constants import MONTH_NAME


def get_declension(month, ending_special, ending_mass):
    """Склонение для имени месяца.

    январь - январе, март - марте и т.д.
    """
    if month in [3, 8]:
        return MONTH_NAME[month] + ending_special
    return regex.sub(r'(\p{L})$', ending_mass, MONTH_NAME[month])


# 1     - день год
# 2-4   - дня года
# 5-20  - дней лет
# 21    - день год
# 22-24 - дня года


def get_full_value_declension(value, type):
    """Возвращает количество дней или лет с правильным падежом."""
    days = ('день', 'дня', 'дней')
    years = ('год', 'года', 'лет')
    word = days if type == 'days' else years

    if value % 10 == 1 and value % 100 != 11:
        need_word = word[0]
    elif 2 <= value % 10 <= 4 and (value % 100 < 10 or value % 100 >= 20):
        need_word = word[1]
    else:
        need_word = word[2]
    return f'{value} {need_word}'
