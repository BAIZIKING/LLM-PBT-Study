from hypothesis import given, strategies as st
import datetime

# Property 1: The output should be a datetime.datetime object.
@given(st.integers(min_value=1, max_value=datetime.datetime.max.toordinal()))
def test_output_is_datetime(ordinal):
    result = datetime.datetime.fromordinal(ordinal)
    assert isinstance(result, datetime.datetime)

# Property 2: The output's ordinal number should always be equal to the ordinal input.
@given(st.integers(min_value=1, max_value=datetime.datetime.max.toordinal()))
def test_output_ordinal_matches_input(ordinal):
    result = datetime.datetime.fromordinal(ordinal)
    assert result.toordinal() == ordinal

# Property 3: The output's hour, minute, second, and microsecond properties should all be 0.
@given(st.integers(min_value=1, max_value=datetime.datetime.max.toordinal()))
def test_output_time_is_midnight(ordinal):
    result = datetime.datetime.fromordinal(ordinal)
    assert result.hour == 0
    assert result.minute == 0
    assert result.second == 0
    assert result.microsecond == 0

# Property 4: The output's tzinfo property should always be None.
@given(st.integers(min_value=1, max_value=datetime.datetime.max.toordinal()))
def test_output_tzinfo_is_none(ordinal):
    result = datetime.datetime.fromordinal(ordinal)
    assert result.tzinfo is None

# Property 5: The output should be within the valid date range in the Gregorian calendar.
@given(st.integers(min_value=1, max_value=datetime.datetime.max.toordinal()))
def test_output_year_in_valid_range(ordinal):
    result = datetime.datetime.fromordinal(ordinal)
    assert datetime.MINYEAR <= result.year <= datetime.MAXYEAR

# End program