from hypothesis import given, strategies as st
import datetime

# Valid ordinal range: 1 <= ordinal <= datetime.max.toordinal()
MIN_ORDINAL = 1
MAX_ORDINAL = datetime.datetime.max.toordinal()


@given(ordinal=st.integers(min_value=MIN_ORDINAL, max_value=MAX_ORDINAL))
def test_datetime_fromordinal_time_components_zero(ordinal):
    # Property 1: hour, minute, second, microsecond are all 0
    result = datetime.datetime.fromordinal(ordinal)
    assert result.hour == 0
    assert result.minute == 0
    assert result.second == 0
    assert result.microsecond == 0


@given(ordinal=st.integers(min_value=MIN_ORDINAL, max_value=MAX_ORDINAL))
def test_datetime_fromordinal_tzinfo_none(ordinal):
    # Property 2: tzinfo is None
    result = datetime.datetime.fromordinal(ordinal)
    assert result.tzinfo is None


@given(ordinal=st.integers(min_value=MIN_ORDINAL, max_value=MAX_ORDINAL))
def test_datetime_fromordinal_roundtrip(ordinal):
    # Property 3: toordinal() returns the original input ordinal
    result = datetime.datetime.fromordinal(ordinal)
    assert result.toordinal() == ordinal


@given(st.data())
def test_datetime_fromordinal_out_of_range_raises(data):
    # Property 4: out-of-range ordinals raise ValueError
    ordinal = data.draw(
        st.one_of(
            st.integers(max_value=MIN_ORDINAL - 1),
            st.integers(min_value=MAX_ORDINAL + 1, max_value=MAX_ORDINAL + 10**6),
        )
    )
    try:
        datetime.datetime.fromordinal(ordinal)
        assert False, "Expected ValueError for out-of-range ordinal"
    except (ValueError, OverflowError):
        pass


@given(ordinal=st.integers(min_value=MIN_ORDINAL, max_value=MAX_ORDINAL))
def test_datetime_fromordinal_matches_date_fromordinal(ordinal):
    # Property 5: date components match date.fromordinal(ordinal)
    result = datetime.datetime.fromordinal(ordinal)
    expected_date = datetime.date.fromordinal(ordinal)
    assert result.year == expected_date.year
    assert result.month == expected_date.month
    assert result.day == expected_date.day
# End program