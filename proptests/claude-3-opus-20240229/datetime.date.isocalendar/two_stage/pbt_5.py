from hypothesis import given, strategies as st
import datetime

@given(st.dates())
def test_isocalendar_returns_named_tuple(date):
    result = date.isocalendar()
    assert isinstance(result, tuple)
    assert hasattr(result, 'year')
    assert hasattr(result, 'week')
    assert hasattr(result, 'weekday')

@given(st.dates())
def test_isocalendar_year_greater_than_or_equal_to_input_year(date):
    result = date.isocalendar()
    assert result.year >= date.year

@given(st.dates())
def test_isocalendar_week_between_1_and_53(date):
    result = date.isocalendar()
    assert 1 <= result.week <= 53

@given(st.dates())
def test_isocalendar_weekday_between_1_and_7(date):
    result = date.isocalendar()
    assert 1 <= result.weekday <= 7

@given(st.dates(), st.integers(min_value=0, max_value=6))
def test_isocalendar_same_week_same_year_and_week(date, days_offset):
    offset_date = date + datetime.timedelta(days=days_offset)
    result1 = date.isocalendar()
    result2 = offset_date.isocalendar()
    if result1.week == result2.week:
        assert result1.year == result2.year
# End program