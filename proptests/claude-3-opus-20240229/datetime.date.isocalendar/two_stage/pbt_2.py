from hypothesis import given, strategies as st
import datetime

@given(st.dates())
def test_isocalendar_returns_named_tuple_with_three_components(d):
    result = d.isocalendar()
    assert isinstance(result, tuple)
    assert len(result) == 3
    assert hasattr(result, 'year')
    assert hasattr(result, 'week')
    assert hasattr(result, 'weekday')

@given(st.dates())
def test_isocalendar_year_greater_than_or_equal_to_input_year(d):
    result = d.isocalendar()
    assert result.year >= d.year

@given(st.dates())
def test_isocalendar_week_between_1_and_53(d):
    result = d.isocalendar()
    assert 1 <= result.week <= 53

@given(st.dates())
def test_isocalendar_weekday_between_1_and_7(d):
    result = d.isocalendar()
    assert 1 <= result.weekday <= 7

@given(st.dates(), st.integers(min_value=0, max_value=6))
def test_isocalendar_same_week_returns_same_year_and_week(d, days_offset):
    d2 = d + datetime.timedelta(days=days_offset)
    iso1 = d.isocalendar()
    iso2 = d2.isocalendar()
    if iso1.week == iso2.week:
        assert iso1.year == iso2.year
# End program