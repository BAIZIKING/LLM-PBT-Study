from hypothesis import given, strategies as st
import datetime

@given(days=st.integers(min_value=0, max_value=365 * 50),  # Up to 50 years
       microseconds=st.integers(min_value=0, max_value=999999))
def test_datetime_timedelta_total_seconds_boundedness(days, microseconds):
    timedelta = datetime.timedelta(days=days, microseconds=microseconds)
    total_seconds = timedelta.total_seconds()
    assert abs(total_seconds - (days * 86400 + microseconds / 1e6)) < 1e-6
# End program