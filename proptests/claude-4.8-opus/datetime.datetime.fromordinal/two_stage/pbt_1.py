from hypothesis import given, strategies as st
import datetime

# Valid ordinal range
MIN_ORD = 1
MAX_ORD = datetime.datetime.max.toordinal()


@given(ordinal=st.integers(min_value=MIN_ORD, max_value=MAX_ORD))
def test_datetime_datetime_fromordinal_time_components_zero(ordinal):
    result = datetime.datetime.fromordinal(ordinal)
    assert result.hour == 0
    assert result.minute == 0
    assert result.second == 0
    assert result.microsecond == 0
# End program


@given(ordinal=st.integers(min_value=MIN_ORD, max_value=MAX_ORD))
def test_datetime_datetime_fromordinal_tzinfo_none(ordinal):
    result = datetime.datetime.fromordinal(ordinal)
    assert result.tzinfo is None
# End program


@given(ordinal=st.integers(min_value=MIN_ORD, max_value=MAX_ORD))
def test_datetime_datetime_fromordinal_roundtrip(ordinal):
    result = datetime.datetime.fromordinal(ordinal)
    assert result.toordinal() == ordinal
# End program


@given(ordinal=st.integers(min_value=MIN_ORD, max_value=MAX_ORD))
def test_datetime_datetime_fromordinal_valid_instance(ordinal):
    result = datetime.datetime.fromordinal(ordinal)
    assert isinstance(result, datetime.datetime)
    assert 1 <= result.year <= 9999
    assert 1 <= result.month <= 12
    assert 1 <= result.day <= 31
# End program


@given(
    ordinal=st.one_of(
        st.integers(max_value=MIN_ORD - 1),
        st.integers(min_value=MAX_ORD + 1, max_value=MAX_ORD + 10**6),
    )
)
def test_datetime_datetime_fromordinal_out_of_range_raises(ordinal):
    try:
        datetime.datetime.fromordinal(ordinal)
        assert False, "Expected ValueError for out-of-range ordinal"
    except (ValueError, OverflowError):
        pass
# End program