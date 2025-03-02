import regex

from constants import MONTH_NAME


def get_declension(month, ending_special, ending_mass):
    """Склонение для имени месяца.

    январь - январе, март - марте и т.д.
    """
    if month in [3, 8]:
        return MONTH_NAME[month] + ending_special
    return regex.sub(r'(\p{L})$', ending_mass, MONTH_NAME[month])


def get_days_declension(days):
    """Склонение для количества дней в месяце.

    28 / 29 / 30 - дней, 31 - день.
    """
    if days == 31:
        return ' день.'
    return ' дней.'
