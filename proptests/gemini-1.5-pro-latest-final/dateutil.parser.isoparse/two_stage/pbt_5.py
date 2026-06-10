from hypothesis import given, strategies as st
import dateutil

# Define strategies for generating valid ISO 8601 datetime strings
date_strategies = st.one_of(
    st.just("YYYY"),
    st.just("YYYY-MM"),
    st.just("YYYYMM"),
    st.just("YYYY-MM-DD"),
    st.just("YYYYMMDD"),
    st.just("YYYY-Www"),
    st.just("YYYYWww"),
    st.just("YYYY-Www-D"),
    st.just("YYYYWwwD"),
)

time_strategies = st.one_of(
    st.just("hh"),
    st.just("hh:mm"),
    st.just("hhmm"),
    st.just("hh:mm:ss"),
    st.just("hhmmss"),
    st.just("hh:mm:ss.ssssss"),
)

timezone_strategies = st.one_of(
    st.just("Z"),
    st.just("+HH:MM"),
    st.just("+HHMM"),
    st.just("+HH"),
    st.just("-HH:MM"),
    st.just("-HHMM"),
    st.just("-HH"),
)

# Generate ISO 8601 datetime strings with optional time and timezone components
@st.composite
def iso_datetime_strings(draw):
    date_str = draw(date_strategies)
    time_str = draw(time_strategies)
    timezone_str = draw(timezone_strategies)
    separator = "T" if time_str else ""  # Add separator only if time is present
    return f"{date_str}{separator}{time_str}{timezone_str}"

@given(iso_datetime_strings())
def test_dateutil_parser_isoparse_output_type(dt_str):
    """Test that the output of isoparse is always a datetime.datetime object."""
    parsed_datetime = dateutil.parser.isoparse(dt_str)
    assert isinstance(parsed_datetime, datetime.datetime)

@given(iso_datetime_strings())
def test_dateutil_parser_isoparse_timezone_handling(dt_str):
    """Test that the tzinfo attribute is set correctly based on the input string."""
    parsed_datetime = dateutil.parser.isoparse(dt_str)
    if "Z" in dt_str or any(tz in dt_str for tz in ["+", "-"]):
        assert parsed_datetime.tzinfo is not None
        assert isinstance(parsed_datetime.tzinfo, (dateutil.tz.tzoffset, dateutil.tz.tzutc))
    else:
        assert parsed_datetime.tzinfo is None

@given(iso_datetime_strings())
def test_dateutil_parser_isoparse_component_values(dt_str):
    """Test that the component values of the output are within valid ranges."""
    parsed_datetime = dateutil.parser.isoparse(dt_str)
    assert 1 <= parsed_datetime.month <= 12
    assert 1 <= parsed_datetime.day <= 31
    assert 0 <= parsed_datetime.hour <= 23
    assert 0 <= parsed_datetime.minute <= 59
    assert 0 <= parsed_datetime.second <= 59
    assert 0 <= parsed_datetime.microsecond <= 999999

@given(iso_datetime_strings())
def test_dateutil_parser_isoparse_date_consistency(dt_str):
    """Test that the date components of the output are consistent with the input."""
    parsed_datetime = dateutil.parser.isoparse(dt_str)
    input_date_str = dt_str.split("T")[0]
    expected_year, expected_month, expected_day = map(int, input_date_str.split("-")[:3])
    assert parsed_datetime.year == expected_year
    assert parsed_datetime.month == expected_month
    assert parsed_datetime.day == expected_day 

@given(iso_datetime_strings())
def test_dateutil_parser_isoparse_time_consistency(dt_str):
    """Test that the time components of the output are consistent with the input."""
    parsed_datetime = dateutil.parser.isoparse(dt_str)
    if "T" in dt_str: 
        input_time_str = dt_str.split("T")[1].split("+")[0] # Ignore timezone for this check 
        expected_hour, expected_minute, *rest = map(int, input_time_str.split(":"))
        assert parsed_datetime.hour == expected_hour
        assert parsed_datetime.minute == expected_minute 
        if rest: 
            expected_second, *rest = rest 
            assert parsed_datetime.second == expected_second 
            if rest:
                expected_microsecond = int(rest[0].ljust(6, '0')) # Pad with zeros for microseconds
                assert parsed_datetime.microsecond == expected_microsecond

# End program