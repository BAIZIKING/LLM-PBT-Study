from hypothesis import given, strategies as st
from datetime import timedelta

@given(st.timedeltas())
def test_total_seconds_output_type(td):
    assert isinstance(td.total_seconds(), float)

@given(st.timedeltas())
def test_total_seconds_non_negative(td):
    assert td.total_seconds() >= 0

@given(st.timedeltas(), st.timedeltas())
def test_total_seconds_additivity(td1, td2):
    assert (td1 + td2).total_seconds() == td1.total_seconds() + td2.total_seconds()

@given(st.timedeltas())
def test_total_seconds_to_hours_conversion(td):
    assert td.total_seconds() / 3600 == td.days * 24 + td.seconds // 3600

@given(st.just(timedelta(0)))
def test_total_seconds_for_zero_timedelta(td):
    assert td.total_seconds() == 0
# End program