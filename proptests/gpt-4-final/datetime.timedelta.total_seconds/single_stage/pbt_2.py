from hypothesis import given, strategies as st
from datetime import timedelta

@given(days=st.integers(min_value=0),
       seconds=st.integers(min_value=0),
       microseconds=st.integers(min_value=0),
       milliseconds=st.integers(min_value=0),
       minutes=st.integers(min_value=0),
       hours=st.integers(min_value=0),
       weeks=st.integers(min_value=0))
def test_timedelta_total_seconds(days, seconds, microseconds, milliseconds,
                                 minutes, hours, weeks):
    td = timedelta(days=days, seconds=seconds, microseconds=microseconds,
                   milliseconds=milliseconds, minutes=minutes,
                   hours=hours, weeks=weeks)

    total_seconds = ((days + weeks * 7) * 24 * 60 * 60 +
                     hours * 60 * 60 +
                     minutes * 60 +
                     seconds +
                     milliseconds / 1000 +
                     microseconds / 1000000)

    # Ensure the total_seconds method returns the correct value.
    assert td.total_seconds() == total_seconds

    # Check whether for time intervals greater than 270 years, the method loses microsecond accuracy.
    if total_seconds > 270 * 365 * 24 * 60 * 60:
        assert round(td.total_seconds()) == round(total_seconds)
    else:
        assert abs(td.total_seconds() - total_seconds) < 0.000001
# End program