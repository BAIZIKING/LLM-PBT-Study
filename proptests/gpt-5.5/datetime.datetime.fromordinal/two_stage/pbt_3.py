from hypothesis import given, strategies as st
import datetime

_MIN_ORDINAL = 1
_MAX_ORDINAL = datetime.datetime.max.toordinal()

@given(st.data())
def test_datetime_datetime_fromordinal_property(data):
    ordinal = data.draw(st.integers(min_value=_MIN_ORDINAL, max_value=_MAX_ORDINAL))
    result = datetime.datetime.fromordinal(ordinal)

    assert isinstance(result, datetime.datetime)
    assert result.toordinal() == ordinal
    assert result.hour == 0
    assert result.minute == 0
    assert result.second == 0
    assert result.microsecond == 0
    assert result.tzinfo is None

    min_result = datetime.datetime.fromordinal(_MIN_ORDINAL)
    assert min_result == datetime.datetime(1, 1, 1, 0, 0)

    max_result = datetime.datetime.fromordinal(_MAX_ORDINAL)
    assert max_result.date() == datetime.datetime.max.date()
    assert max_result.hour == 0
    assert max_result.minute == 0
    assert max_result.second == 0
    assert max_result.microsecond == 0
    assert max_result.tzinfo is None

# End program