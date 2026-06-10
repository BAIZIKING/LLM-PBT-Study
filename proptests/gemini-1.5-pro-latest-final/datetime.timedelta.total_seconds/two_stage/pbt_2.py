from hypothesis import given, strategies as st
import datetime

# Define a strategy for generating timedelta objects, avoiding overflow issues
def timedelta_strategy():
    days = st.integers(min_value=0, max_value=270*365) # Limit days to avoid overflow
    seconds = st.floats(min_value=0, max_value=86400) # Limit seconds to a day's range
    microseconds = st.integers(min_value=0, max_value=10**6)
    return st.builds(datetime.timedelta, days=days, seconds=seconds, microseconds=microseconds)

@given(timedelta_strategy())
def test_timedelta_total_seconds_non_negative(td):
    assert td.total_seconds() >= 0

@given(st.data())
def test_timedelta_total_seconds_monotonic(data):
    td1 = data.draw(timedelta_strategy())
    td2 = data.draw(timedelta_strategy())
    assume(td1 <= td2)
    assert td1.total_seconds() <= td2.total_seconds()

@given(st.data())
def test_timedelta_total_seconds_scaling(data):
    td = data.draw(timedelta_strategy())
    factor = data.draw(st.floats(min_value=0, allow_nan=False, allow_infinity=False))
    assert (td * factor).total_seconds() == td.total_seconds() * factor

@given(st.data())
def test_timedelta_total_seconds_addition(data):
    td1 = data.draw(timedelta_strategy())
    td2 = data.draw(timedelta_strategy())
    assert (td1 + td2).total_seconds() == td1.total_seconds() + td2.total_seconds()

# Due to potential microsecond inaccuracies, we test for approximate equality
@given(st.data())
def test_timedelta_total_seconds_large_delta(data):
    years = data.draw(st.integers(min_value=271, max_value=300))
    td = datetime.timedelta(days=years*365)
    expected_seconds = years * 365 * 24 * 60 * 60
    assert abs(td.total_seconds() - expected_seconds) < 1e-3 # Allow for some microsecond error

# End program