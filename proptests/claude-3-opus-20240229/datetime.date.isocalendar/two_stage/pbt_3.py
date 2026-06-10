from hypothesis import given, strategies as st
import datetime

@given(st.dates())
def test_isocalendar_year_greater_than_or_equal_to_date_year(date):
    iso_year, _, _ = date.isocalendar()
    assert iso_year >= date.year

@given(st.dates())
def test_isocalendar_week_between_1_and_53(date):
    _, iso_week, _ = date.isocalendar()
    assert 1 <= iso_week <= 53

@given(st.dates())
def test_isocalendar_weekday_between_1_and_7(date):
    _, _, iso_weekday = date.isocalendar()
    assert 1 <= iso_weekday <= 7

@given(st.integers(min_value=1, max_value=9999))
def test_isocalendar_first_day_of_iso_year_week_is_1(year):
    first_day = datetime.date(year, 1, 1)
    while first_day.weekday() != 0:
        first_day += datetime.timedelta(days=1)
    _, iso_week, _ = first_day.isocalendar()
    assert iso_week == 1

@given(st.dates(), st.integers(min_value=0, max_value=6))
def test_isocalendar_same_week_dates_have_same_year_and_week(date, days_offset):
    offset_date = date + datetime.timedelta(days=days_offset)
    iso_year, iso_week, _ = date.isocalendar()
    offset_iso_year, offset_iso_week, _ = offset_date.isocalendar()
    assert (iso_year, iso_week) == (offset_iso_year, offset_iso_week)
# End program