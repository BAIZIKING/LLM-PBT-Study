from hypothesis import given, strategies as st
import datetime
import math

@given(st.timedeltas())
def test_total_seconds_output_type(td):
    assert isinstance(td.total_seconds(), float)

@given(st.timedeltas())
def test_total_seconds_equivalent_to_division(td):
    assert td.total_seconds() == td / datetime.timedelta(seconds=1)

@given(st.timedeltas())
def test_total_seconds_sign(td):
    if td >= datetime.timedelta(0):
        assert td.total_seconds() >= 0
    else:
        assert td.total_seconds() < 0

@given(st.integers(min_value=-999999999, max_value=999999999),
       st.integers(min_value=0, max_value=86399),
       st.integers(min_value=0, max_value=999999))
def test_total_seconds_sum_of_components(days, seconds, microseconds):
    td = datetime.timedelta(days=days, seconds=seconds, microseconds=microseconds)
    expected_total_seconds = days * 86400 + seconds + microseconds / 1e6
    assert math.isclose(td.total_seconds(), expected_total_seconds, rel_tol=1e-9)

@given(st.timedeltas(max_value=datetime.timedelta(days=270*365)))
def test_total_seconds_microsecond_accuracy(td):
    expected_total_seconds = (td.days * 86400 + td.seconds + td.microseconds / 1e6)
    assert math.isclose(td.total_seconds(), expected_total_seconds, abs_tol=1e-6)
# End program