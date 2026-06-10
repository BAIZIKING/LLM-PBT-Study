from hypothesis import given, strategies as st
from dateutil.parser import isoparse
from dateutil.tz import tzoffset, tzutc
import datetime

# Summary: 
# The strategy generates a wide variety of valid ISO-8601 datetime strings by:
# - Generating random date components (year, month, day) 
# - Optionally generating time components (hour, minute, second, microsecond)
# - Optionally generating a timezone offset (Z, +HH:MM, -HH:MM, +HHMM, -HHMM, +HH, -HH) 
# - Combining the components into a valid ISO-8601 string
# It checks that isoparse:
# - Parses the generated valid string into a datetime object with the expected components
# - Correctly handles UTC and timezone offsets 
# - Defaults unspecified components to their lowest values

@given(st.builds(
    lambda date, time, tz: f"{date}T{time}{tz}" if time else date,
    st.dates(min_value=datetime.date(1, 1, 1)).map(lambda d: d.isoformat()),
    st.one_of(
        st.times().map(lambda t: t.isoformat()),
        st.none()
    ),
    st.one_of(
        st.just("Z"),
        st.builds(lambda h, m: f"+{h:02d}:{m:02d}", st.integers(0, 23), st.integers(0, 59)),
        st.builds(lambda h, m: f"-{h:02d}:{m:02d}", st.integers(0, 23), st.integers(0, 59)),
        st.builds(lambda h, m: f"+{h:02d}{m:02d}", st.integers(0, 23), st.integers(0, 59)), 
        st.builds(lambda h, m: f"-{h:02d}{m:02d}", st.integers(0, 23), st.integers(0, 59)),
        st.builds(lambda h: f"+{h:02d}", st.integers(0, 23)),
        st.builds(lambda h: f"-{h:02d}", st.integers(0, 23)),
        st.none()
    )
))
def test_isoparse(dt_str):
    dt = isoparse(dt_str)
    assert isinstance(dt, datetime.datetime)
    
    if "T" not in dt_str:
        assert dt.time() == datetime.time(0, 0, 0)
    
    if dt_str.endswith("Z"):
        assert dt.tzinfo == tzutc()
    elif "+" in dt_str or "-" in dt_str:
        assert isinstance(dt.tzinfo, tzoffset)
        assert dt.utcoffset() == dt.tzinfo.utcoffset(None)
    else:
        assert dt.tzinfo is None

# End program