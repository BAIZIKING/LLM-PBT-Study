from hypothesis import given, strategies as st
import datetime

@given(st.timedeltas())
def test_total_seconds_returns_float(td):
    assert isinstance(td.total_seconds(), float)

@given(st.timedeltas(min_value=datetime.timedelta(0)))
def test_total_seconds_non_negative_for_non_negative_input(td):
    assert td.total_seconds() >= 0

@given(st.timedeltas())
def test_total_seconds_equals_total_seconds_represented(td):
    total_seconds = td.days * 86400 + td.seconds + td.microseconds / 1e6
    assert abs(td.total_seconds() - total_seconds) < 1e-6

@given(st.timedeltas(), st.timedeltas())
def test_total_seconds_preserves_order(t1, t2):
    if t1 > t2:
        assert t1.total_seconds() > t2.total_seconds()

@given(st.timedeltas(max_value=datetime.timedelta(days=270*365)))
def test_total_seconds_roundtrip(td):
    td_from_seconds = datetime.timedelta(seconds=td.total_seconds())
    assert td == td_from_seconds
# End program