from hypothesis import given, strategies as st
import datetime

# Define a strategy for generating valid ordinal values within a reasonable range
ordinal_strategy = st.integers(min_value=1, max_value=datetime.date.max.toordinal() - 1000)

@given(ordinal_strategy)
def test_datetime_fromordinal_type(ordinal):
    result = datetime.datetime.fromordinal(ordinal)
    assert isinstance(result, datetime.datetime)

@given(ordinal_strategy)
def test_datetime_fromordinal_time_components(ordinal):
    result = datetime.datetime.fromordinal(ordinal)
    assert result.hour == result.minute == result.second == result.microsecond == 0

@given(ordinal_strategy)
def test_datetime_fromordinal_timezone(ordinal):
    result = datetime.datetime.fromordinal(ordinal)
    assert result.tzinfo is None

@given(ordinal_strategy)
def test_datetime_fromordinal_consistency(ordinal):
    result = datetime.datetime.fromordinal(ordinal)
    assert result.toordinal() == ordinal

@given(ordinal_strategy)
def test_datetime_fromordinal_date_consistency(ordinal):
    result = datetime.datetime.fromordinal(ordinal)
    expected_date = datetime.date.fromordinal(ordinal)
    assert (result.year, result.month, result.day) == (expected_date.year, expected_date.month, expected_date.day)
# End program