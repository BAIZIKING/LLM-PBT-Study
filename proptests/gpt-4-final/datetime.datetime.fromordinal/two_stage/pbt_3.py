from hypothesis import given, strategies as st
import datetime

# Property 1: The output is a datetime object
@given(st.integers(min_value=1, max_value=datetime.datetime.max.toordinal()))
def test_output_is_datetime(ordinal):
    result = datetime.datetime.fromordinal(ordinal)
    assert isinstance(result, datetime.datetime)

# Property 2: The output is a valid date
@given(st.integers(min_value=1, max_value=datetime.datetime.max.toordinal()))
def test_output_is_valid_date(ordinal):
    result = datetime.datetime.fromordinal(ordinal)
    try:
        datetime.datetime(result.year, result.month, result.day)
    except ValueError:
        assert False

# Property 3: The output is not timezone-aware
@given(st.integers(min_value=1, max_value=datetime.datetime.max.toordinal()))
def test_output_is_not_timezone_aware(ordinal):
    result = datetime.datetime.fromordinal(ordinal)
    assert result.tzinfo is None

# Property 4: The output time is always midnight
@given(st.integers(min_value=1, max_value=datetime.datetime.max.toordinal()))
def test_output_time_is_midnight(ordinal):
    result = datetime.datetime.fromordinal(ordinal)
    assert result.hour == 0 and result.minute == 0 and result.second == 0 and result.microsecond == 0

# Property 5: The date corresponds to the input ordinal
@given(st.integers(min_value=1, max_value=datetime.datetime.max.toordinal()))
def test_date_corresponds_to_input_ordinal(ordinal):
    result = datetime.datetime.fromordinal(ordinal)
    assert result.toordinal() == ordinal
# End program