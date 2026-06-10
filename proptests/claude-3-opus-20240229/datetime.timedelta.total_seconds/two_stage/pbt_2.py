from hypothesis import given, strategies as st
import datetime

@given(st.timedeltas())
def test_total_seconds_returns_float(td):
    assert isinstance(td.total_seconds(), float)

@given(st.timedeltas(min_value=datetime.timedelta(0)))
def test_total_seconds_positive_timedelta_returns_positive(td):
    assert td.total_seconds() >= 0

@given(st.timedeltas(max_value=datetime.timedelta(0)))
def test_total_seconds_negative_timedelta_returns_negative(td):
    assert td.total_seconds() <= 0

@given(st.timedeltas())
def test_total_seconds_matches_division(td):
    assert abs(td.total_seconds() - (td / datetime.timedelta(seconds=1))) < 1e-6

@given(st.timedeltas(), st.timedeltas())
def test_total_seconds_preserves_ordering(td1, td2):
    if td1 > td2:
        assert td1.total_seconds() > td2.total_seconds()
# End program