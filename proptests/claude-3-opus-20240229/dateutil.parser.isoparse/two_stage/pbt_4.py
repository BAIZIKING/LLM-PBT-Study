from hypothesis import given, strategies as st
from datetime import datetime
import dateutil.parser
import dateutil.tz

@given(st.from_regex(r"\d{4}(-\d{2}(-\d{2})?)?"))
def test_isoparse_returns_datetime(dt_str):
    parsed_dt = dateutil.parser.isoparse(dt_str)
    assert isinstance(parsed_dt, datetime)

@given(st.from_regex(r"\d{4}(-\d{2}(-\d{2})?)?"))
def test_isoparse_date_components(dt_str):
    parsed_dt = dateutil.parser.isoparse(dt_str)
    assert parsed_dt.year == int(dt_str[:4])
    if len(dt_str) >= 7:
        assert parsed_dt.month == int(dt_str[5:7])
    if len(dt_str) >= 10:
        assert parsed_dt.day == int(dt_str[8:10])

@given(st.from_regex(r"\d{4}-\d{2}-\d{2}T\d{2}(:\d{2}(:\d{2}(\.\d{1,6})?)?)?"))
def test_isoparse_time_components(dt_str):
    parsed_dt = dateutil.parser.isoparse(dt_str)
    time_portion = dt_str.split("T")[1]
    assert parsed_dt.hour == int(time_portion[:2])
    if len(time_portion) >= 5:
        assert parsed_dt.minute == int(time_portion[3:5])
    if len(time_portion) >= 8:
        assert parsed_dt.second == int(time_portion[6:8])
    if "." in time_portion:
        assert parsed_dt.microsecond == int(time_portion.split(".")[1].ljust(6, "0"))

@given(st.from_regex(r"\d{4}-\d{2}-\d{2}T\d{2}(:\d{2}(:\d{2}(\.\d{1,6})?)?)?(Z|[+-]\d{2}(:?\d{2})?)?"))
def test_isoparse_timezone(dt_str):
    parsed_dt = dateutil.parser.isoparse(dt_str)
    if dt_str.endswith("Z"):
        assert parsed_dt.tzinfo == dateutil.tz.UTC
    elif "+" in dt_str or "-" in dt_str:
        offset_str = dt_str.split("+-")[-1]
        if ":" in offset_str:
            hours, minutes = map(int, offset_str.split(":"))
        else:
            hours, minutes = int(offset_str[:2]), int(offset_str[2:] or 0)
        offset = dateutil.tz.tzoffset(None, hours * 3600 + minutes * 60)
        assert parsed_dt.tzinfo == offset
    else:
        assert parsed_dt.tzinfo is None

@given(st.from_regex(r"\d{4}(-\d{2}(-\d{2})?)?"))
def test_isoparse_naive_datetime(dt_str):
    parsed_dt = dateutil.parser.isoparse(dt_str)
    assert parsed_dt.tzinfo is None
# End program