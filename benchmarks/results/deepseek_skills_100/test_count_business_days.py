import pytest

from count_business_days import count_business_days


class TestCountBusinessDays:
    def test_single_full_week(self):
        # 2026-12-14 (пн) -> 2026-12-21 (пн): 5 рабочих дней
        assert count_business_days('2026-12-14', '2026-12-21') == 5

    def test_two_full_weeks(self):
        # 2026-12-14 (пн) -> 2026-12-28 (пн): 10 рабочих дней
        assert count_business_days('2026-12-14', '2026-12-28') == 10

    def test_weekend_only(self):
        # 2026-12-19 (сб) -> 2026-12-21 (пн): 0 рабочих дней
        assert count_business_days('2026-12-19', '2026-12-21') == 0

    def test_same_day(self):
        # Полуоткрытый интервал: пустой
        assert count_business_days('2026-12-15', '2026-12-15') == 0

    def test_end_before_start(self):
        assert count_business_days('2026-12-20', '2026-12-15') == 0

    def test_monday_to_friday(self):
        # 2026-12-14 (пн) -> 2026-12-18 (пт): 4 рабочих дня (пн, вт, ср, чт)
        assert count_business_days('2026-12-14', '2026-12-18') == 4

    def test_friday_to_monday(self):
        # 2026-12-18 (пт) -> 2026-12-21 (пн): 1 рабочий день (пт)
        assert count_business_days('2026-12-18', '2026-12-21') == 1

    def test_saturday_to_sunday(self):
        # 2026-12-19 (сб) -> 2026-12-20 (вс): 0
        assert count_business_days('2026-12-19', '2026-12-20') == 0

    def test_sunday_to_monday(self):
        # 2026-12-20 (вс) -> 2026-12-21 (пн): 0
        assert count_business_days('2026-12-20', '2026-12-21') == 0

    def test_cross_month(self):
        # 2026-12-15 (вт) -> 2027-01-15 (пт)
        # Дней: 31. Полных недель: 4 (28 дней) -> 20 рабочих.
        # Остаток 3 дня: 2027-01-12 (вт), 13 (ср), 14 (чт) -> 3 рабочих.
        # Итого 23.
        assert count_business_days('2026-12-15', '2027-01-15') == 23

    def test_cross_year_full_week(self):
        # 2026-12-28 (пн) -> 2027-01-04 (пн): 5 рабочих дней
        assert count_business_days('2026-12-28', '2027-01-04') == 5

    def test_leap_year_february(self):
        # 2028-02-01 (вт) -> 2028-03-01 (ср)
        # Дней: 29. Полных недель: 4 (28 дней) -> 20 рабочих.
        # Остаток 1 день: 2028-02-29 (вт) -> 1 рабочий.
        # Итого 21.
        assert count_business_days('2028-02-01', '2028-03-01') == 21

    def test_invalid_date_format(self):
        with pytest.raises(ValueError):
            count_business_days('15-12-2026', '2027-01-15')

    def test_invalid_end_date_format(self):
        with pytest.raises(ValueError):
            count_business_days('2026-12-15', 'not-a-date')

    def test_returns_int(self):
        result = count_business_days('2026-12-14', '2026-12-21')
        assert isinstance(result, int)
