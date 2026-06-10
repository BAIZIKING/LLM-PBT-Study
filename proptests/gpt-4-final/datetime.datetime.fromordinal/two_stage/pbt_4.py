from hypothesis import given, strategies as st
import datetime

@given(st.integers(min_value=1, max_value=datetime.datetime.max.toordinal()))
def test_fromordinal_valid_datetime(input):
    result = datetime.datetime.fromordinal(input)
    assert isinstance(result, datetime.datetime)

@given(st.integers(min_value=1, max_value=datetime.datetime.max.toordinal()))
def test_fromordinal_time_zero(input):
    result = datetime.datetime.fromordinal(input)
    assert result.hour == result.minute == result.second == result.microsecond == 0

@given(st.integers(min_value=1, max_value=datetime.datetime.max.toordinal()))
def test_fromordinal_tzinfo_none(input):
    result = datetime.datetime.fromordinal(input)
    assert result.tzinfo is None

@given(st.integers(min_value=1, max_value=datetime.datetime.max.toordinal()))
def test_fromordinal_ordinal_match(input):
    result = datetime.datetime.fromordinal(input)
    assert result.toordinal() == input
	
@given(st.integers(max_value=0).map(abs))
def test_fromordinal_valueerror_negative(input):
    try:
        _ = datetime.datetime.fromordinal(input)
        assert False, "Should have thrown ValueError"
    except ValueError:
        pass

@given(st.integers(min_value=datetime.datetime.max.toordinal()+1))
def test_fromordinal_valueerror_large(input):
    try:
        _ = datetime.datetime.fromordinal(input)
        assert False, "Should have thrown ValueError"
    except ValueError:
        pass