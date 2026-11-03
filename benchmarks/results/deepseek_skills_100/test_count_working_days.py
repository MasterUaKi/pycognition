import pytest

from count_working_days import count_working_days


class TestCountWorkingDays:
    def test_single_working_day(self):
        # Понедельник
        assert count_working_days("2024-01-01", "2024-01-01") == 1

    def test_single_weekend_day_saturday(self):
        # Суббота
        assert count_working_days("2024-01-06", "2024-01-06") == 0

    def test_single_weekend_day_sunday(self):
        # Воскресенье
        assert count_working_days("2024-01-07", "2024-01-07") == 0

    def test_full_week(self):
        # Понедельник — воскресенье
        assert count_working_days("2024-01-01", "2024-01-07") == 5

    def test_two_full_weeks(self):
        assert count_working_days("2024-01-01", "2024-01-14") == 10

    def test_weekend_only(self):
        # Суббота — воскресенье
        assert count_working_days("2024-01-06", "2024-01-07") == 0

    def test_partial_week_starting_saturday(self):
        # Суббота — среда
        assert count_working_days("2024-01-06", "2024-01-10") == 3

    def test_partial_week_starting_sunday(self):
        # Воскресенье — четверг
        assert count_working_days("2024-01-07", "2024-01-11") == 4

    def test_month_period(self):
        # Январь 2024: 23 рабочих дня
        assert count_working_days("2024-01-01", "2024-01-31") == 23

    def test_leap_year_february(self):
        # Февраль 2024 (високосный): 21 рабочий день
        assert count_working_days("2024-02-01", "2024-02-29") == 21

    def test_year_period(self):
        # 2024 год: 262 рабочих дня
        assert count_working_days("2024-01-01", "2024-12-31") == 262

    def test_start_after_end_raises(self):
        with pytest.raises(ValueError):
            count_working_days("2024-01-10", "2024-01-01")

    def test_invalid_format_raises(self):
        with pytest.raises(ValueError):
            count_working_days("01-01-2024", "2024-01-10")

    def test_invalid_date_raises(self):
        with pytest.raises(ValueError):
            count_working_days("2024-13-01", "2024-12-31")

    def test_same_weekend_boundary(self):
        # Пятница — понедельник
        assert count_working_days("2024-01-05", "2024-01-08") == 2
