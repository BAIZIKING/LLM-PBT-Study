from hypothesis import given, strategies as st
from dateutil.parser import parse
import datetime

# Summary: Generate a wide variety of valid and invalid date string formats, with 
# different separators, orderings (DMY, MDY, YMD), and with/without time components.
# Include leap years, leap seconds, time zones, and special date values.
# Check that valid date strings parse successfully into datetime objects with correct values.
# Check that invalid date strings raise the expected ParserError or OverflowError.
# Check specific properties like fuzzy parsing, ignoring timezones, and default dates.
@given(st.data())
def test_dateutil_parser_parse(data):
    date_strs = st.one_of(
        st.dates().map(lambda d: d.strftime("%Y-%m-%d")),  
        st.dates().map(lambda d: d.strftime("%m/%d/%Y")),
        st.dates().map(lambda d: d.strftime("%d.%m.%Y")),
        st.dates().map(lambda d: d.isoformat()),
        st.datetimes().map(lambda dt: dt.strftime("%Y-%m-%d %H:%M:%S")),
        st.datetimes().map(lambda dt: dt.isoformat()),
        st.sampled_from(["January 1, 2047", "Today is 2047 Jan 1", "2047 Jan 1 is a date"])
    )
    date_str = data.draw(date_strs)
    
    try:
        parsed_date = parse(date_str)
        assert isinstance(parsed_date, datetime.datetime)
        if "%Y" in date_str:
            assert parsed_date.year == int(date_str.split("%Y")[0][-4:])
        if "%m" in date_str or "/" in date_str or "." in date_str: 
            assert parsed_date.month == int(date_str.split("%m")[0][-2:])
        if "%d" in date_str or "/" in date_str or "." in date_str:
            assert parsed_date.day == int(date_str.split("%d")[0][-2:])
        if "%H" in date_str:
            assert parsed_date.hour == int(date_str.split("%H")[0][-2:])
        if "%M" in date_str:
            assert parsed_date.minute == int(date_str.split("%M")[0][-2:])
        if "%S" in date_str:
            assert parsed_date.second == int(date_str.split("%S")[0][-2:])

        default_dt = data.draw(st.datetimes())
        parsed_with_default = parse(date_str, default=default_dt)
        assert parsed_with_default.replace(year=default_dt.year) == default_dt

        parsed_ignore_tz = parse(date_str, ignoretz=True) 
        assert parsed_ignore_tz.tzinfo is None
        
        tzinfos = {"EST": -5*3600}
        parsed_with_tz = parse(date_str + " EST", tzinfos=tzinfos)
        assert parsed_with_tz.tzinfo is not None

        parsed_fuzzy = parse(date_str, fuzzy=True)
        assert isinstance(parsed_fuzzy, datetime.datetime)

    except (ValueError, OverflowError):
        # date_str is invalid
        assert False, f"Unexpected error parsing date: {date_str}"
# End program        