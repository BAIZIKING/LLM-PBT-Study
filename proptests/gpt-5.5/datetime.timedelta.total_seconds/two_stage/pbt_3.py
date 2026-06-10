from hypothesis import given, strategies as st
import datetime

_SAFE_DAYS = 50_000

def safe_timedeltas():
    return st.builds(
        datetime.timedelta,
        days=st.integers(min_value=-_SAFE_DAYS, max_value=_SAFE_DAYS),
        seconds=st.integers(min_value=0, max_value=86_399),
        microseconds=st.integers(min_value=0, max_value=999_999),
    )

@given(st.data())
def test_datetime_timedelta_total_seconds_returns_float(data):
    td = data.draw(safe_timedeltas())
    result = td.total_seconds()
    assert isinstance(result, float)

@given(st.data())
def test_datetime_timedelta_total_seconds_equals_division_by_one_second(data):
    td = data.draw(safe_timedeltas())
    result = td.total_seconds()
    expected = td / datetime.timedelta(seconds=1)
    assert result == expected

@given(st.data())
def test_datetime_timedelta_total_seconds_matches_components(data):
    td = data.draw(safe_timedeltas())
    result = td.total_seconds()
    expected = td.days * 86_400 + td.seconds + td.microseconds / 1_000_000
    assert abs(result - expected) <= 1e-6

@given(st.data())
def test_datetime_timedelta_total_seconds_zero_is_zero_float(data):
    result = datetime.timedelta(0).total_seconds()
    assert result == 0.0
    assert isinstance(result, float)

@given(st.data())
def test_datetime_timedelta_total_seconds_preserves_sign_and_equality(data):
    td = data.draw(safe_timedeltas())
    result = td.total_seconds()

    if td > datetime.timedelta(0):
        assert result > 0.0
    elif td < datetime.timedelta(0):
        assert result < 0.0
    else:
        assert result == 0.0

    total_microseconds = (
        (td.days * 86_400 + td.seconds) * 1_000_000
        + td.microseconds
    )
    equivalent_td = datetime.timedelta(microseconds=total_microseconds)

    assert td == equivalent_td
    assert td.total_seconds() == equivalent_td.total_seconds()
# End program