from hypothesis import given, strategies as st
import datetime

@given(st.dates())
def test_datetime_date_isocalendar_property_5(d: datetime.date):
    tomorrow = d + datetime.timedelta(days=1)
    today_result = d.isocalendar()
    tomorrow_result = tomorrow.isocalendar()
    if today_result.weekday == 7:
        assert tomorrow_result.weekday == 1
    else:
        assert tomorrow_result.weekday == today_result.weekday + 1
# End program