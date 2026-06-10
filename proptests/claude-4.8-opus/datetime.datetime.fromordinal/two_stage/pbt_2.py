from hypothesis import given, strategies as st
import datetime

# Valid ordinal range: 1 <= ordinal <= datetime.max.toordinal()
MIN_ORDINAL = 1
MAX_ORDINAL = datetime.datetime.max.toordinal()


@given(ordinal=st.integers(min_value=MIN_ORDINAL, max_value=MAX_ORDINAL))
def test_datetime_datetime_fromordinal_time_fields_zero(ordinal):
    result = datetime.datetime.fromordinal(ordinal)
    assert isinstance(result, datetime.datetime)
    assert result.hour == 0
    assert result.minute == 0
    assert result.second == 0
    assert result.microsecond == 0


@given(ordinal=st.integers(min_value=MIN_ORDINAL, max_value=MAX_ORDINAL))
def test_datetime_datetime_fromordinal_tzinfo_none(ordinal):
    result = datetime.datetime.fromordinal(ordinal)
    assert result.tzinfo is None


@given(ordinal=st.integers(min_value=MIN_ORDINAL, max_value=MAX_ORDINAL))
def test_datetime_datetime_fromordinal_roundtrip(ordinal):
    result = datetime.datetime.fromordinal(ordinal)
    assert result.toordinal() == ordinal


@given(
    ordinal=st.one_of(
        st.integers(max_value=MIN_ORDINAL - 1),
        st.integers(min_value=MAX_ORDINAL + 1),
    )
)
def test_datetime_datetime_fromordinal_out_of_range_raises(ordinal):
    try:
        datetime.datetime.fromordinal(ordinal)
        assert False, "Expected ValueError for out-of-range ordinal"
    except (ValueError, OverflowError):
        pass


@given(ordinal=st.integers(min_value=MIN_ORDINAL, max_value=MAX_ORDINAL - 1))
def test_datetime_datetime_fromordinal_monotonic_consecutive(ordinal):
    current = datetime.datetime.fromordinal(ordinal)
    nxt = datetime.datetime.fromordinal(ordinal + 1)
    assert nxt > current
    assert nxt - current == datetime.timedelta(days=1)
# End program