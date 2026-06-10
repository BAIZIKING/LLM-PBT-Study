from hypothesis import given, strategies as st
import datetime

@given(st.integers(min_value=1, max_value=datetime.datetime.max.toordinal()))
def test_datetime_fromordinal_return_type(ordinal):
    result = datetime.datetime.fromordinal(ordinal)
    assert isinstance(result, datetime.datetime)

@given(st.integers(min_value=1, max_value=datetime.datetime.max.toordinal()))
def test_datetime_fromordinal_zero_time(ordinal):
    result = datetime.datetime.fromordinal(ordinal)
    assert result.hour == 0
    assert result.minute == 0
    assert result.second == 0
    assert result.microsecond == 0

@given(st.integers(min_value=1, max_value=datetime.datetime.max.toordinal()))
def test_datetime_fromordinal_tzinfo(ordinal):
    result = datetime.datetime.fromordinal(ordinal)
    assert result.tzinfo is None

@given(st.integers(min_value=1, max_value=datetime.datetime.max.toordinal()))
def test_datetime_fromordinal_date(ordinal):
    result = datetime.datetime.fromordinal(ordinal)
    assert ordinal == result.toordinal()

@given(st.integers())
def test_datetime_fromordinal_raise_valueerror(ordinal):
    if ordinal < 1 or ordinal > datetime.datetime.max.toordinal():
        with pytest.raises(ValueError):
            datetime.datetime.fromordinal(ordinal)
    else:
        assert isinstance(datetime.datetime.fromordinal(ordinal), datetime.datetime)
# End program