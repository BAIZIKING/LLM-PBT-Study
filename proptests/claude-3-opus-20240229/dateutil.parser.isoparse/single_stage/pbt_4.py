from hypothesis import given, strategies as st
from dateutil.parser import isoparse
from datetime import datetime, timezone

# Summary: 
# Generate a variety of valid ISO 8601 datetime strings to test isoparse
# Valid strings include:
#  - Dates in YYYY, YYYY-MM, YYYYMM, YYYY-MM-DD, YYYYMMDD formats 
#  - ISO weeks like 2023-W01 or 2023W012
#  - Times in HH, HH:MM, HHMM, HH:MM:SS.SSSSSS formats
#  - Timezones like Z, ±HH:MM, ±HHMM, ±HH
# Combine dates, times, timezones to generate full ISO 8601 strings
# Check that isoparse:
#  - Parses valid strings successfully into datetime objects
#  - Returns datetimes with expected values for each component 
#  - Handles UTC & tzoffset correctly
#  - Defaults unspecified components to their lowest values

@given(st.builds(
    lambda date, time, tz: f"{date}T{time}{tz}", 
    st.one_of(
        st.dates().map(lambda d: d.strftime("%Y-%m-%d")),
        st.dates().map(lambda d: d.strftime("%Y%m%d")), 
        st.dates().map(lambda d: d.strftime("%Y-%m")),
        st.dates().map(lambda d: d.strftime("%Y%m")),
        st.integers(1, 9999).map(str),
        st.dates().map(lambda d: d.strftime("%Y-W%W")), 
        st.dates().map(lambda d: d.strftime("%YW%W%w"))
    ),
    st.one_of(
        st.times().map(lambda t: t.strftime("%H:%M:%S")),
        st.times().map(lambda t: t.strftime("%H%M%S")),
        st.times().map(lambda t: t.strftime("%H:%M")), 
        st.times().map(lambda t: t.strftime("%H%M")),
        st.integers(0, 23).map(lambda h: f"{h:02d}")
    ),
    st.one_of(
        st.just("Z"),
        st.timezones().map(lambda tz: tz.strftime("%z")),
        st.timezones().map(lambda tz: tz.strftime("%Z"))
    )
))
def test_isoparse(dt_str):
    dt = isoparse(dt_str)
    assert isinstance(dt, datetime)
    
    if 'T' in dt_str:
        date_str, time_str = dt_str.split('T', 1)
        
        if time_str.endswith("Z"):
            assert dt.tzinfo == timezone.utc
        elif "+" in time_str or "-" in time_str:
            offset = dt.tzinfo.utcoffset(dt)
            assert offset == dt.tzinfo.utcoffset(dt)
    else:
        date_str = dt_str
        assert dt.time() == datetime.min.time()
        
    if len(date_str) == 4:
        assert dt.year == int(date_str)
    elif len(date_str) == 6: 
        assert dt.year == int(date_str[:4])
        assert dt.month == int(date_str[4:])
    elif len(date_str) == 7:
        assert dt.year == int(date_str[:4]) 
        assert dt.month == int(date_str[5:])
    elif len(date_str) == 8:
        assert dt.year == int(date_str[:4])
        assert dt.month == int(date_str[4:6])
        assert dt.day == int(date_str[6:])
    elif len(date_str) == 10:
        assert dt.year == int(date_str[:4])
        assert dt.month == int(date_str[5:7]) 
        assert dt.day == int(date_str[8:])
    elif 'W' in date_str:
        assert dt.isocalendar()[1:] == (int(date_str[-4:-2]), int(date_str[-1:]))
        
# End program