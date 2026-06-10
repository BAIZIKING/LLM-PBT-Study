from hypothesis import given, strategies as st
import dateutil

# Define strategies for generating ISO 8601 date and time components
date_strategies = {
    "YYYY": st.integers(min_value=1, max_value=9999),
    "MM": st.integers(min_value=1, max_value=12),
    "DD": st.integers(min_value=1, max_value=31),
    "hh": st.integers(min_value=0, max_value=23),
    "mm": st.integers(min_value=0, max_value=59),
    "ss": st.integers(min_value=0, max_value=59),
}

# Strategy for generating optional time zone offsets
timezone_strategy = st.one_of(
    st.just("Z"),
    st.integers(min_value=-14, max_value=14).map(lambda x: f"{x:+03d}:00"),
    st.integers(min_value=-14, max_value=14).map(lambda x: f"{x:+03d}"),
)

# Build strategy for complete ISO 8601 datetime strings
datetime_strategy = st.builds(
    lambda YYYY, MM, DD, hh, mm, ss, tz: f"{YYYY}-{MM:02d}-{DD:02d}T{hh:02d}:{mm:02d}:{ss:02d}{tz}",
    **date_strategies,
    tz=timezone_strategy,
)

# 1. Output Type Property
@given(datetime_strategy)
def test_output_type(dt_str):
    parsed_datetime = dateutil.parser.isoparse(dt_str)
    assert isinstance(parsed_datetime, dateutil.parser.datetime)

# 2. Time Zone Representation Property
@given(datetime_strategy)
def test_timezone_representation(dt_str):
    parsed_datetime = dateutil.parser.isoparse(dt_str)
    if dt_str.endswith("Z"):
        assert isinstance(parsed_datetime.tzinfo, dateutil.tz.tzutc)
    elif any(char in dt_str for char in "+-"):
        assert isinstance(parsed_datetime.tzinfo, dateutil.tz.tzoffset)
    else:
        assert parsed_datetime.tzinfo is None

# 3. Year Consistency Property
@given(datetime_strategy)
def test_year_consistency(dt_str):
    parsed_datetime = dateutil.parser.isoparse(dt_str)
    assert parsed_datetime.year == int(dt_str[:4])

# 4. Monotonicity Property
@given(
    st.tuples(datetime_strategy, datetime_strategy).filter(
        lambda x: x[0][:19] == x[1][:19] and x[0] < x[1]
    )
)
def test_monotonicity(dates):
    dt_str1, dt_str2 = dates
    parsed_datetime1 = dateutil.parser.isoparse(dt_str1)
    parsed_datetime2 = dateutil.parser.isoparse(dt_str2)
    assert parsed_datetime1 < parsed_datetime2

# 5. Unspecified Component Defaults Property
@given(st.sampled_from(["YYYY", "YYYY-MM", "YYYY-MM-DD"]))
def test_unspecified_defaults(date_format):
    date_str = st.builds(lambda year, month, day: f"{year}-{month:02d}-{day:02d}", **{k: v for k, v in date_strategies.items() if k in date_format}).example()
    parsed_datetime = dateutil.parser.isoparse(date_str)
    assert (parsed_datetime.hour, parsed_datetime.minute, parsed_datetime.second, parsed_datetime.microsecond) == (0, 0, 0, 0)
    if len(date_str) <= 7:  # YYYY or YYYY-MM format
        assert parsed_datetime.day == 1
    if len(date_str) <= 4:  # YYYY format
        assert (parsed_datetime.month, parsed_datetime.day) == (1, 1)
# End program