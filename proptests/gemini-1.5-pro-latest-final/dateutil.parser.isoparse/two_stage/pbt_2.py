from hypothesis import given, strategies as st
import dateutil

# Define strategies for generating ISO 8601 date and time components
date_strategies = st.tuples(
    st.integers(min_value=1, max_value=9999),  # Year
    st.integers(min_value=1, max_value=12),  # Month
    st.integers(min_value=1, max_value=31),  # Day
)
time_strategies = st.tuples(
    st.integers(min_value=0, max_value=23),  # Hour
    st.integers(min_value=0, max_value=59),  # Minute
    st.integers(min_value=0, max_value=59),  # Second
    st.integers(min_value=0, max_value=999999)  # Microsecond
)
timezone_strategies = st.one_of(
    st.just('Z'),
    st.integers(min_value=-14, max_value=14).map(lambda x: f"{x:+03d}"),
    st.tuples(
        st.integers(min_value=-14, max_value=14),
        st.integers(min_value=0, max_value=59)
    ).map(lambda x: f"{x[0]:+03d}:{x[1]:02d}")
)

@given(
    date=date_strategies, 
    time=time_strategies, 
    timezone=timezone_strategies,
    separator=st.sampled_from(['T', ' '])
)
def test_dateutil_parser_isoparse_properties(date, time, timezone, separator):
    # Generate ISO 8601 string
    date_str = f"{date[0]:04d}-{date[1]:02d}-{date[2]:02d}"
    time_str = f"{time[0]:02d}:{time[1]:02d}:{time[2]:02d}.{time[3]:06d}"
    iso_str = f"{date_str}{separator}{time_str}{timezone}"

    # Parse the string
    dt_obj = dateutil.parser.isoparse(iso_str)
    
    # Property 1: Output Type
    assert isinstance(dt_obj, dateutil.parser._parser.ParserError) or isinstance(dt_obj, datetime.datetime)

    # Remaining properties only apply if parsing was successful 
    if isinstance(dt_obj, datetime.datetime):

        # Property 2: Time Components 
        assert dt_obj.hour == time[0]
        assert dt_obj.minute == time[1]
        assert dt_obj.second == time[2]
        assert dt_obj.microsecond == time[3]

        # Property 3: Date Components
        assert dt_obj.year == date[0]
        assert dt_obj.month == date[1]
        assert dt_obj.day == date[2]

        # Property 4: Unspecified Components - Not tested here as the strategy always generates complete dates and times

        # Property 5: Time Zone
        if timezone == 'Z':
            assert dt_obj.tzinfo == dateutil.tz.tzutc() 
        else:
            assert isinstance(dt_obj.tzinfo, dateutil.tz.tzoffset)

# End program 