from hypothesis import given, strategies as st
from dateutil.parser import isoparse
from dateutil.tz import tzutc, tzoffset
import datetime

# Property 1: The output must be a datetime.datetime object
@given(st.text(min_size=4, max_size=10))
def test_output_date_type(dt_str):
    assert isinstance(isoparse(dt_str), datetime.datetime)

# Property 2: Unspecified time defaults to 00:00:00
@given(st.text(min_size=10, max_size=10))
def test_unspecified_time(dt_str):
    assert isoparse(dt_str).time() == datetime.time(0, 0)

# Property 3: UTC time zone representation
@given(st.text(min_size=6, max_size=6))
def test_utc_tzinfo_representation(dt_str):
    assert isinstance(isoparse(dt_str).tzinfo, tzutc)

# Property 4: Verify ISO week and day format
@given(st.from_regex("^\\d{4}-W\\d{2}-\\d$", fullmatch=True))
def test_iso_week_day(dt_str):
    datetime_obj = isoparse(dt_str)
    iso_year, iso_week, iso_day = datetime_obj.isocalendar()
    assert f"{iso_year}-W{iso_week:02d}-{iso_day}" == dt_str

# Property 5: Verify fractional seconds
@given(st.from_regex("^\\d{2}:\\d{2}:\\d{2}\\.\\d{1,6}$", fullmatch=True))
def test_fractional_seconds(dt_str):
    datetime_obj = isoparse(dt_str)
    assert datetime_obj.microsecond != 0