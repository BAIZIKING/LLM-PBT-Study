from hypothesis import given, strategies as st
import datetime

@given(st.dates())
def test_datetime_date_isocalendar_property_5(dt):
    dt2 = dt + datetime.timedelta(days=7)
    result1 = dt.isocalendar()
    result2 = dt2.isocalendar()
    assert result1.weekday == result2.weekday
# End program 