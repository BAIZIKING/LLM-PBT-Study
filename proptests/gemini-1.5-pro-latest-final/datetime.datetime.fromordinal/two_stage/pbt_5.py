from hypothesis import given, strategies as st
import datetime

@given(st.integers(min_value=1, max_value=datetime.MAXYEAR))  # Strategy adjusted for valid ordinal range
def test_datetime_fromordinal_type(ordinal):
    result = datetime.datetime.fromordinal(ordinal)
    assert isinstance(result, datetime.datetime)

@given(st.integers(min_value=1, max_value=datetime.MAXYEAR))
def test_datetime_fromordinal_time_components(ordinal):
    result = datetime.datetime.fromordinal(ordinal)
    assert result.hour == 0
    assert result.minute == 0
    assert result.second == 0
    assert result.microsecond == 0

@given(st.integers(min_value=1, max_value=datetime.MAXYEAR))
def test_datetime_fromordinal_timezone(ordinal):
    result = datetime.datetime.fromordinal(ordinal)
    assert result.tzinfo is None

@given(st.integers(min_value=1, max_value=datetime.MAXYEAR))
def test_datetime_fromordinal_ordinal_relationship(ordinal):
    result = datetime.datetime.fromordinal(ordinal)
    assert result.toordinal() == ordinal

@given(st.integers(min_value=1, max_value=datetime.MAXYEAR))
def test_datetime_fromordinal_date_consistency(ordinal):
    result = datetime.datetime.fromordinal(ordinal)
    assert datetime.datetime.fromordinal(result.toordinal()) == result 
# End program