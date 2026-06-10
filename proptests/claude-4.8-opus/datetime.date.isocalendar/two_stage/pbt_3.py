from hypothesis import given, strategies as st
import datetime

# Strategy for generating valid dates within the supported range.
date_strategy = st.dates(
    min_value=datetime.date.min,
    max_value=datetime.date.max,
)

@given(d=date_strategy)
def test_isocalendar_returns_named_tuple_with_three_fields(d):
    # Property 1: The output is a named tuple with exactly three components
    # named year, week, and weekday.
    result = d.isocalendar()
    assert len(result) == 3
    assert hasattr(result, "year")
    assert hasattr(result, "week")
    assert hasattr(result, "weekday")
    # Verify tuple unpacking matches named access
    year, week, weekday = result
    assert year == result.year
    assert week == result.week
    assert weekday == result.weekday


@given(d=date_strategy)
def test_isocalendar_weekday_in_range(d):
    # Property 2: weekday is always an integer between 1 and 7 inclusive.
    result = d.isocalendar()
    assert isinstance(result.weekday, int)
    assert 1 <= result.weekday <= 7


@given(d=date_strategy)
def test_isocalendar_week_in_range(d):
    # Property 3: week is always an integer between 1 and 53 inclusive.
    result = d.isocalendar()
    assert isinstance(result.week, int)
    assert 1 <= result.week <= 53


@given(d=date_strategy)
def test_isocalendar_year_close_to_gregorian_year(d):
    # Property 4: the ISO year is always within 1 of the Gregorian year.
    result = d.isocalendar()
    assert isinstance(result.year, int)
    assert abs(result.year - d.year) <= 1


@given(d=date_strategy)
def test_isocalendar_roundtrip(d):
    # Property 5: reconstructing a date from the ISO calendar output
    # via fromisocalendar returns the original date.
    year, week, weekday = d.isocalendar()
    reconstructed = datetime.date.fromisocalendar(year, week, weekday)
    assert reconstructed == d
# End program