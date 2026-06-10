from hypothesis import given, strategies as st
import datetime

SAFE_MIN = datetime.timedelta(days=-1000)
SAFE_MAX = datetime.timedelta(days=1000)
FULL_MIN = datetime.timedelta.min
FULL_MAX = datetime.timedelta.max


@given(st.data())
def test_datetime_timedelta_total_seconds_returns_float_property(data):
    td = data.draw(st.timedeltas(min_value=FULL_MIN, max_value=FULL_MAX))
    result = td.total_seconds()

    assert isinstance(result, float)


@given(st.data())
def test_datetime_timedelta_total_seconds_equivalent_to_division_property(data):
    td = data.draw(st.timedeltas(min_value=FULL_MIN, max_value=FULL_MAX))
    result = td.total_seconds()
    expected = td / datetime.timedelta(seconds=1)

    assert result == expected


@given(st.data())
def test_datetime_timedelta_total_seconds_matches_components_property(data):
    td = data.draw(st.timedeltas(min_value=SAFE_MIN, max_value=SAFE_MAX))
    result = td.total_seconds()
    expected = td.days * 86400 + td.seconds + td.microseconds / 1_000_000

    assert abs(result - expected) <= 1e-6


@given(st.data())
def test_datetime_timedelta_total_seconds_sign_matches_duration_property(data):
    td = data.draw(st.timedeltas(min_value=FULL_MIN, max_value=FULL_MAX))
    result = td.total_seconds()
    zero = datetime.timedelta(0)

    if td > zero:
        assert result > 0.0
    elif td < zero:
        assert result < 0.0
    else:
        assert result == 0.0


@given(st.data())
def test_datetime_timedelta_total_seconds_additivity_property(data):
    a = data.draw(st.timedeltas(min_value=SAFE_MIN, max_value=SAFE_MAX))
    b = data.draw(st.timedeltas(min_value=SAFE_MIN, max_value=SAFE_MAX))

    result = (a + b).total_seconds()
    expected = a.total_seconds() + b.total_seconds()

    assert abs(result - expected) <= 1e-6


# End program