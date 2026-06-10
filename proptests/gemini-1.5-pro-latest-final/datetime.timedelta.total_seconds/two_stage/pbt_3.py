from hypothesis import given, strategies as st
import datetime

# Define strategies for generating timedeltas
timedelta_strategy = st.builds(datetime.timedelta, 
                                days=st.integers(min_value=0),
                                hours=st.integers(min_value=0, max_value=23),
                                minutes=st.integers(min_value=0, max_value=59),
                                seconds=st.integers(min_value=0, max_value=59),
                                microseconds=st.integers(min_value=0, max_value=999999))

@given(timedelta=timedelta_strategy)
def test_total_seconds_is_float(timedelta):
    """Output is a floating-point number."""
    assert isinstance(timedelta.total_seconds(), float)

@given(timedelta=timedelta_strategy)
def test_non_negative_timedelta(timedelta):
    """Output is non-negative for non-negative timedeltas."""
    assert timedelta.total_seconds() >= 0

@given(timedelta=timedelta_strategy, factor=st.floats(min_value=0, allow_nan=False, allow_infinity=False))
def test_scaling_behavior(timedelta, factor):
    """Scaling behavior: Multiplying a timedelta by a positive constant scales the output."""
    scaled_timedelta = factor * timedelta
    assert scaled_timedelta.total_seconds() == factor * timedelta.total_seconds()

@given(timedelta1=timedelta_strategy, timedelta2=timedelta_strategy)
def test_summation_property(timedelta1, timedelta2):
    """Summation property: total_seconds() of sum equals sum of total_seconds()."""
    assert timedelta1.total_seconds() + timedelta2.total_seconds() == (timedelta1 + timedelta2).total_seconds()

# Testing microsecond accuracy limitations is complex and platform-dependent, 
# and might require specific strategies based on system limitations.
# It's recommended to consult the documentation and platform specifics for accurate testing. 
# End program 