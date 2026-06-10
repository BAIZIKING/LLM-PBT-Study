from hypothesis import given, strategies as st
import datetime

@given(st.dates(), st.integers(min_value=0, max_value=6))
def test_isocalendar_same_week(dt: datetime.date, days_diff: int):
    dt2 = dt + datetime.timedelta(days=days_diff)
    result1 = dt.isocalendar()
    result2 = dt2.isocalendar()
    assert result1.week == result2.week
# End program