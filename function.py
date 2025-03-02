import calendar
import re
from datetime import date

from constants import DAY_NAME, MAX_YEAR, MDAYS, MIN_YEAR
from substitutions import get_declension, get_days_declension


class Event:
    """Событие для отслеживания.

    Если есть special_rule и не указан week_number -> последняя неделя месяца.
    """

    def __init__(
            self,
            day_and_month,
            description,
            year=None,
            special_rule=False,
            week_number=None
    ):
        """Инициализатор нового события."""
        self.day_and_month = day_and_month
        self.year = year
        self.description = description
        self.special_rule = special_rule
        self.week_number = week_number
        self._validate_date()

    # FIXME здесь только дата - а нужно событие.
    def __repr__(self):
        """Отображение даты."""
        data = f'{self._day}.{self._month}'
        if self.__year_in_data():
            data += f'.{self._year}'
        return data

    def _validate_date(self):
        """Проверяет в полях «day_and_month» и «year» вводимую информацию."""
        pattern = r'^(\d{2})(\d{2})$'
        pair = re.match(pattern, str(self.day_and_month))
        if not pair:
            raise ValueError(
                f'Указано некорректное значение «{self.day_and_month}». '
                f'Нужно 4 цифры вида ДДММ.'
            )
        day, month = [int(x) for x in pair.groups()]

        if not (1 <= month <= 12):
            raise ValueError(f'Месяца {month} нет.')

        if self.year:
            if str(self.year).isdigit():
                if not MIN_YEAR <= int(self.year) <= MAX_YEAR:
                    raise ValueError(
                        f'Год {self.year} не подходит. '
                        f'Диапазон {MIN_YEAR}-{MAX_YEAR}.'
                    )
            else:
                raise ValueError(f'Неверный формат года ({self.year})?')
            self._year = int(self.year)

        if not (day <= MDAYS[month]):
            add_year = ''
            added_day = 0
            if self.year:
                add_year = f'{self.year} года '
                if calendar.isleap(int(self.year)) and month == 2:
                    added_day = 1
            raise ValueError(
                f'В {get_declension(month, "е", "е")} {add_year}только '
                f'{MDAYS[month] + added_day}'
                f'{get_days_declension(MDAYS[month])}'
            )
        self._day = day
        self._month = month
        return self

    def _year_in_data(self):
        """Возвращает True, если в указанной дате есть год."""
        return (True if hasattr(self, '_year') else False)

    def _get_weekday(self, number=False):
        """Возвращает день недели вида пн-вс. При number=True - число 0-6."""
        if self._year_in_data():
            weekday = date.weekday(date(ev._year, ev._month, ev._day))
            return weekday if number else DAY_NAME[weekday]

    def _get_days_in_month(self):
        """Возвращает количество дней в указанном месяце."""
        return 29 if (
            calendar.isleap(self._year) and self._month == 2
        ) else MDAYS[self._month]

    def as_view(self):
        """Отображение события вида «1 января 2025г. - день Х».

        Если указан год - то считается количество прошедших лет.
        """
        data = f'{self._day} {get_declension(self._month, "а", "я")}'
        if self._year_in_data():
            year_pass = date.today().year - self._year  # прошло лет
            return f'{data} - {self.description} ({year_pass} лет)'
        return f'{data} - {self.description}'

    # def __str__(self):
    #     return f'{date(self.year, r'self.day_and_month')

    def get_events_special_params(self):
        """Получает параметры для специальных дат (если они есть).

        1. Указанный месяц (1-12)
        2. Номер дня недели (0-6)
        3. Номер недели месяца для нужного дня (1-6)
        4. Общее количество недель в месяце (4-6).
        """
        if not self.special_rule:
            return None

        # Номер искомого дня в недели
        this_weekday = self._get_weekday(True)

        # Какой по счёту этот this_weekday в месяце:
        first_day_of_month = date(self._year, self._month, 1).weekday()
        days_in_first_week = 7 - first_day_of_month  # дней в 1-ой неделе.
        number_of_week = 1 if self._day <= days_in_first_week else (
            (self._day - days_in_first_week - 1) // 7 + 2
        )

        # Всего недель в искомом месяце:
        all_weeks_in_month = (
            (self._get_days_in_month() - days_in_first_week + 6) // 7 + 1
        )

        return {
            'this_month': self._month,
            'this_weekday': this_weekday,
            'number_of_week_for_this_day': number_of_week,
            'all_weeks_in_month': all_weeks_in_month
        }


ev = Event('3011', 'день матери', '2025', True)

print(ev.get_events_special_params())
