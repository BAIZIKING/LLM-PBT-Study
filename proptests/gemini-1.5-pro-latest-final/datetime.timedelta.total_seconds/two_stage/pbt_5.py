from hypothesis import given, strategies as st
import datetime

# Define strategy for generating timedeltas with limited magnitude to avoid overflows
timedelta_strategy = st.builds(datetime.timedelta, 
                              days=st.integers(min_value=-36500, max_value=36500),
                              seconds=st.integers(min_value=0, max_value=86399),
                              microseconds=st.integers(min_value=0, max_value=999999))

@given(timedelta_strategy)
def test_total_seconds_is_float(td):
    assert isinstance(td.total_seconds(), float)

@given(timedelta_strategy)
def test_total_seconds_non_negative(td):
    assert td.total_seconds() >= 0

@given(timedelta_strategy, st.floats(min_value=0.001, max_value=100))
def test_total_seconds_scaling(td, factor):
    scaled_td = factor * td
    assert scaled_td.total_seconds() == td.total_seconds() * factor

@given(timedelta_strategy, timedelta_strategy)
def test_total_seconds_arithmetic(td1, td2):
    assert (td1 + td2).total_seconds() == td1.total_seconds() + td2.total_seconds()
    assert (td1 - td2).total_seconds() == td1.total_seconds() - td2.total_seconds()

# Testing loss of accuracy for large time intervals is complex and requires specialized strategies and assertions.  
# This example focuses on the core properties demonstrable through Hypothesis.

# End program