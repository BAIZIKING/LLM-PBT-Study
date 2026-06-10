from hypothesis import given, strategies as st
import datetime

@given(st.dates())
def test_isocalendar_returns_named_tuple_with_three_components(date):
    result = date.isocalendar()
    assert isinstance(result, tuple)
    assert len(result) == 3
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
def test_isocalendar_same_week_returns_same_year_and_week(date, days_offset):
    date2 = date + datetime.timedelta(days=days_offset)
    if date.isocalendar().week == date2.isocalendar().week:
        assert date.isocalendar().year == date2.isocalendar().year
        assert date.isocalendar().week == date2.isocalendar().week
# End program