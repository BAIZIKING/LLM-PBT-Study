from hypothesis import given, strategies as st
from dateutil.parser import isoparse
from datetime import datetime

# Summary: 
# Generate a variety of valid ISO 8601 datetime strings, including:
# - Various date formats (YYYY, YYYY-MM, YYYY-MM-DD)
# - With and without time components of increasing precision
# - Different valid time zone offsets
# Check that isoparse successfully parses them to datetime objects
# and unspecified components default to their lowest values.
@given(st.builds(
    lambda date, time, tz: date + ("T" + time if time else "") + tz,
    st.one_of(st.just("2023"), st.just("2023-04"), st.just("2023-04-28")),  
    st.one_of(st.just(""), st.just("08"), st.just("08:15"), 
              st.just("08:15:30"), st.just("08:15:30.123456")),
    st.one_of(st.just(""), st.just("Z"), st.just("+01:00"), st.just("+0100"))
))
def test_dateutil_parser_isoparse(dt_str):
    dt = isoparse(dt_str)
    assert isinstance(dt, datetime)
    
    if len(dt_str) == 4:
        assert dt.month == 1 and dt.day == 1 and dt.hour == 0
    elif len(dt_str) == 7: 
        assert dt.day == 1 and dt.hour == 0
    elif 'T' not in dt_str:
        assert dt.hour == 0
    
    if 'Z' in dt_str or '+00:00' in dt_str or '+0000' in dt_str:
        assert dt.tzinfo is not None and dt.tzinfo.utcoffset(dt).total_seconds() == 0
# End program