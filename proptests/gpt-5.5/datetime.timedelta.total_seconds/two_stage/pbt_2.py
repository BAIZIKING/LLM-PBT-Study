from hypothesis import given, strategies as st
import datetime

_VALID_TIMEDELTAS = st.builds(
    datetime.timedelta,
    days=st.integers(min_value=-999_999_999, max_value=999_999_999),
    seconds=st.integers(min_value=0, max_value=86_399),
    microseconds=st.integers(min_value=0, max_value=999_999),
)

_BOUNDED_TIMEDELTAS = st.builds(
    datetime.timedelta,
    days=st.integers(min_value=-(365 * 250), max_value=365 * 250),
    seconds=st.integers(min_value=0, max_value=86_399),
    microseconds=st.integers(min_value=0, max_value=999_999),
)

@given(st.data())
def test_datetime_timedelta_total_seconds_returns_float(data):
    td = data.draw(_VALID_TIMEDELTAS)
    result = td.total_seconds()
    assert isinstance(result, float)

@given(st.data())
def test_datetime_timedelta_total_seconds_equivalent_to_division_by_one_second(data):
    td = data.draw(_VALID_TIMEDELTAS)
    result = td.total_seconds()
    expected = td / datetime.timedelta(seconds=1)
    assert result == expected

@given(st.data())
def test_datetime_timedelta_total_seconds_matches_component_formula(data):
    td = data.draw(_BOUNDED_TIMEDELTAS)
    result = td.total_seconds()
    expected = td.days * 86_400 + td.seconds + td.microseconds / 1_000_000
    assert abs(result - expected) <= 1e-6

@given(st.data())
def test_datetime_timedelta_total_seconds_zero_is_zero_float(data):
    td = datetime.timedelta(0)
    result = td.total_seconds()
    assert result == 0.0
    assert isinstance(result, float)

@given(st.data())
def test_datetime_timedelta_total_seconds_sign_matches_timedelta_sign(data):
    td = data.draw(_VALID_TIMEDELTAS)
    result = td.total_seconds()

    if td > datetime.timedelta(0):
        assert result > 0.0
    elif td < datetime.timedelta(0):
        assert result < 0.0
    else:
        assert result == 0.0

# End program