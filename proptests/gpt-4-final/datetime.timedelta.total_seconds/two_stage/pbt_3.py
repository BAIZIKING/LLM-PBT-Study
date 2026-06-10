from hypothesis import given, strategies as st
import datetime

# Test 1: Equality
@given(st.integers(min_value=0, max_value=3600))
def test_timedelta_total_seconds_equality(minutes):
    td = datetime.timedelta(minutes=minutes)
    assert td.total_seconds() == minutes * 60

# Test 2: Type
@given(st.integers(min_value=0))
def test_timedelta_total_seconds_type(seconds):
    td = datetime.timedelta(seconds=seconds)
    assert isinstance(td.total_seconds(), float)

# Test 3: Non-Negativity
@given(st.integers(min_value=0))
def test_timedelta_total_seconds_non_negativity(days):
    td = datetime.timedelta(days=days)
    assert td.total_seconds() >= 0

# Test 4: Consistency
@given(st.integers(min_value=0, max_value=365))
def test_timedelta_total_seconds_consistency(days):
    td = datetime.timedelta(days=days)
    assert td.total_seconds() == td.total_seconds()

# Test 5: Scale
@given(st.tuples(st.integers(min_value=0, max_value=10), st.integers(min_value=1, max_value=10)))
def test_timedelta_total_seconds_scale(values):
    td1 = datetime.timedelta(days=values[0])
    td2 = datetime.timedelta(days=values[0] * values[1])
    assert td1.total_seconds() * values[1] == td2.total_seconds()
# End program