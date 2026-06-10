from hypothesis import given, strategies as st
import dateutil

# Define strategies for generating ISO 8601 date and time strings
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
    st.integers(min_value=-23, max_value=23).map(lambda x: f"{x:+03d}"),
    st.integers(min_value=-23, max_value=23).map(lambda x: f"{x:+03d}:00"),
    st.integers(min_value=-23, max_value=23).map(lambda x: f"{x:+03d}00"),
)

# Combine strategies to generate complete ISO 8601 datetime strings
datetime_strategy = st.builds(
    lambda date, time, sep, tz: f"{date}{sep}{time}{tz}",
    date_strategies,
    time_strategies,
    st.one_of(st.just("T"), st.just("")),  # Separator between date and time
    timezone_strategies,
)


@given(datetime_strategy)
def test_dateutil_parser_isoparse_output_type(dt_str):
    """Output of isoparse is always a datetime.datetime object."""
    parsed_datetime = dateutil.parser.isoparse(dt_str)
    assert isinstance(parsed_datetime, datetime.datetime)


@given(datetime_strategy.filter(lambda x: "T" in x and ":" in x.split("T")[1]))
def test_dateutil_parser_isoparse_time_components(dt_str):
    """Time components are correctly parsed from the input string."""
    parsed_datetime = dateutil.parser.isoparse(dt_str)
    _, time_str = dt_str.split("T")
    hours, minutes, *rest = map(int, time_str.split(":"))
    assert parsed_datetime.hour == hours
    assert parsed_datetime.minute == minutes
    if rest:
        seconds = int(rest[0])
        assert parsed_datetime.second == seconds
        if len(rest) > 1:
            microseconds = int(rest[1].replace(".", "").replace(",", ""))
            assert parsed_datetime.microsecond == microseconds


@given(
    datetime_strategy.filter(
        lambda x: any(
            pattern in x for pattern in ["YYYY-MM", "YYYYMM", "YYYY-MM-DD", "YYYYMMDD"]
        )
    )
)
def test_dateutil_parser_isoparse_date_components(dt_str):
    """Date components are correctly parsed from the input string."""
    parsed_datetime = dateutil.parser.isoparse(dt_str)
    date_str, *_ = dt_str.split("T")
    year, month, *day = map(int, date_str.split("-") + date_str.split("W"))
    assert parsed_datetime.year == year
    assert parsed_datetime.month == month
    if day:
        assert parsed_datetime.day == day[0]


@given(datetime_strategy.filter(lambda x: x.endswith("Z") or "+" in x or "-" in x))
def test_dateutil_parser_isoparse_timezone_information(dt_str):
    """Timezone information is correctly parsed and represented."""
    parsed_datetime = dateutil.parser.isoparse(dt_str)
    if dt_str.endswith("Z"):
        assert isinstance(parsed_datetime.tzinfo, dateutil.tz.tzutc)
    else:
        assert isinstance(parsed_datetime.tzinfo, dateutil.tz.tzoffset)


@given(datetime_strategy)
def test_dateutil_parser_isoparse_minimum_values(dt_str):
    """Missing components have their minimum possible values."""
    parsed_datetime = dateutil.parser.isoparse(dt_str)
    if "T" not in dt_str:
        assert parsed_datetime.hour == 0
        assert parsed_datetime.minute == 0
        assert parsed_datetime.second == 0
        assert parsed_datetime.microsecond == 0
    if all(pattern not in dt_str for pattern in ["YYYY-MM", "YYYYMM"]):
        assert parsed_datetime.month == 1
    if all(
        pattern not in dt_str for pattern in ["YYYY-MM-DD", "YYYYMMDD", "YYYYWwwD"]
    ):
        assert parsed_datetime.day == 1
# End program