import calendar
import logging
import re
from datetime import date
from typing import Union

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

# FIXME in def _validated_date:
# надо добавить проверку, когда не указан номер недели, но есть дата -
# чтобы дата была последним именованным днем месяца.

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

        # В случае, если год не указывается - подставляется текущий год:
        if not self.year:
            # today_year = date.today().year
            # self.year = today_year
            # logging.WARNING(f'Год не был указан, установлен {today_year}')

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

        # Проверка, что указанный день есть в указанном месяце/годе:
        if not (day <= MDAYS[month]):
            add_year = ''  # Заглушка на случай, когда год не указан.
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

    def _year_in_data(self) -> bool:
        """Возвращает True, если в указанной дате есть год."""
        return (True if hasattr(self, '_year') else False)

    def _get_weekday(self, number: bool = False) -> Union[str, int]:
        """Возвращает день недели вида пн-вс. При number=True - число 0-6."""
        if not self._year_in_data():
            raise ValueError('Год не был указан!')
        # if self._year_in_data():
        weekday = date.weekday(date(*self._y_m_d()))
        return weekday if number else DAY_NAME[weekday]

    def _get_firstday(self, year, month) -> int:
        """Возвращает номер (0-6) первого дня (для нужного месяца и года)."""
        return date(year, month, 1).weekday()

    def _get_days_in_month(self) -> int:
        """Возвращает количество дней в указанном месяце."""
        return 29 if (
            calendar.isleap(self._year) and self._month == 2
        ) else MDAYS[self._month]

    def _y_m_d(self) -> tuple[int, int, int]:
        """Возвращает кортеж вида ГГГГ ММ ДД."""
        return (self._year, self._month, self._day)

    def as_view(self) -> str:
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
            return {}

        # Номер искомого дня в недели
        this_weekday = self._get_weekday(True)

        # Какой по счёту этот this_weekday в месяце:
        first_day_of_month = self._get_firstday(self._year, self._month)
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

    def _create_rules_for_events_with_special_params(self, last_week=False):
        """Создает для события со специальными параметрами новую запись."""
        if date.today().year == int(self.year):  # текущий год == указанному

            # если сегодня день - меньше, чем день события:
            if date.today().timetuple().tm_yday < (
                date(*self._y_m_d()).timetuple().tm_yday
            ):
                pass  # действие не требуется

            # когда года совпадают и надо переписывать системно:
            next_year = int(self._year) + 1
            rules = self.get_events_special_params()
            month = rules['this_month']
            this_weekday = rules['this_weekday']
            if last_week:
                number_of_week_for_this_day = rules['all_weeks_in_month']
            number_of_week_for_this_day = rules['number_of_week_for_this_day']

            first_day_of_month_in_next_year = self._get_firstday(
                next_year, month)

            _ = 1 if first_day_of_month_in_next_year >= this_weekday else 0
            day = 7 * (number_of_week_for_this_day + _) - (
                first_day_of_month_in_next_year
            ) + this_weekday - 6
            return (day, month, next_year)  # заглушка
            return Event(
                f'{day:02d}{month:02d}',
                self.description,
                next_year,
                self.special_rule,
                self.week_number
            )
        return self  # FIXME пока заглушка
        # return 'это в будущем - ждём' if (
        #     date.today().year < int(self.year)
        # ) else 'это в прошлом - укажите дату из будущего'

    def create_rules_for_events_with_special_params(self):
        """Валидирует и создает событию со спец.параметрами новую запись.

        Если в первоначальной записи указаны специальные правила:
            - если в записи не указан номер недели - значит последняя неделя.
        """
        if self.special_rule:
            if not self.week_number:
                self._create_rules_for_events_with_special_params(True)
            self._create_rules_for_events_with_special_params()
        return self


ev = Event('1901', 'день матери', None, True, 3)
print(ev.create_rules_for_events_with_special_params())
