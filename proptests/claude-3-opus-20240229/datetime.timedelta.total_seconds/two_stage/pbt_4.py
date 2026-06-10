from hypothesis import given, strategies as st
import datetime

@given(st.timedeltas())
def test_total_seconds_returns_float(td):
    assert isinstance(td.total_seconds(), float)

@given(st.timedeltas())
def test_total_seconds_non_negative(td):
    assert td.total_seconds() >= 0

@given(st.timedeltas())
def test_total_seconds_equals_division(td):
    assert td.total_seconds() == td / datetime.timedelta(seconds=1)

@given(st.integers(min_value=0, max_value=1000000))
def test_total_seconds_from_whole_seconds(seconds):
    td = datetime.timedelta(seconds=seconds)
    assert td.total_seconds() == float(seconds)

@given(st.timedeltas(), st.timedeltas())
def test_total_seconds_additive_property(t1, t2):
    assert (t1 + t2).total_seconds() == t1.total_seconds() + t2.total_seconds()
# End program