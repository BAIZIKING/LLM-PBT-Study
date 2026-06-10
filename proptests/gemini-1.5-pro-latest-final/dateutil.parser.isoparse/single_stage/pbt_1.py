from hypothesis import given, strategies as st
from dateutil.parser import isoparse
from dateutil.tz import tzoffset, tzutc

# Summary: Generates random ISO 8601 datetime strings with various formats and edge cases.
@given(st.data())
def test_dateutil_parser_isoparse(data):
    # Generate date components
    year = data.draw(st.integers(min_value=1900, max_value=2100))
    month = data.draw(st.integers(min_value=1, max_value=12))
    day = data.draw(st.integers(min_value=1, max_value=28))  # Handle Feb separately
    week = data.draw(st.integers(min_value=1, max_value=53))
    weekday = data.draw(st.integers(min_value=1, max_value=7))

    # Generate time components
    hour = data.draw(st.integers(min_value=0, max_value=24))  # Handle midnight
    minute = data.draw(st.integers(min_value=0, max_value=59))
    second = data.draw(st.integers(min_value=0, max_value=59))
    microsecond = data.draw(st.integers(min_value=0, max_value=999999))

    # Choose separators and formats
    separator = data.draw(st.sampled_from(["T", " "]))
    date_format = data.draw(
        st.sampled_from(["YYYY-MM-DD", "YYYYMMDD", "YYYY-Www-D", "YYYYWwwD"])
    )
    time_format = data.draw(st.sampled_from(["hh:mm:ss.ssssss", "hhmmss", "hh:mm", "hh"]))

    # Generate time zone offset
    tz_offset = data.draw(
        st.one_of(
            st.just("Z"),
            st.integers(min_value=-12, max_value=14).map(lambda h: f"{h:+}"),  # ±HH
            st.tuples(
                st.integers(min_value=-12, max_value=14),
                st.integers(min_value=0, max_value=59),
            ).map(lambda h, m: f"{h:+}:{m:02}"),  # ±HH:MM
            st.tuples(
                st.integers(min_value=-12, max_value=14),
                st.integers(min_value=0, max_value=59),
            ).map(lambda h, m: f"{h:02}{m:02}"),  # ±HHMM
        )
    )
    # ... (rest of the code continues below) 