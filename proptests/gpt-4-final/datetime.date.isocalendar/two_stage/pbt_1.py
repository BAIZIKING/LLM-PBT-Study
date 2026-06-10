from hypothesis import given, strategies as st
import datetime

# Generate a strategy for generating date objects
dates = st.dates(min_value=datetime.date.min, max_value=datetime.date.max)

@given(dates)
def test_isocalendar_type(date):
    result = date.isocalendar()
    assert isinstance(result, datetime.IsoCalendarDate)

@given(dates)
def test_isocalendar_year_range(date):
    result = date.isocalendar()
    assert 1 <= result.year <= 9999

@given(dates)
def test_isocalendar_week_range(date):
    result = date.isocalendar()
    assert 1 <= result.week <= 53

@given(dates)
def test_isocalendar_weekday_range(date):
    result = date.isocalendar()
    assert 1 <= result.weekday <= 7

@given(dates)
def test_isocalendar_ISO_calendar_logic(date):
    result = date.isocalendar()
    if date.month == 1 and date.day == 1 and result.weekday == 5:
        assert result.year == date.year + 1
    else:
        assert result.year == date.year