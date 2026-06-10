import datetime
from hypothesis import given, strategies as st

DATE_FORMATS = ['%Y', '%Y-%m', '%Y-%m-%d', '%YW%W', '%YW%W-%w']
TIME_FORMATS =['%H', '%H:%M', '%H:%M:%S', '%H:%M:%S.%f']

@given(
    date_format = st.sampled_from(DATE_FORMATS),
    time_format = st.sampled_from(TIME_FORMATS),
    tz = st.booleans()
)
def test_dateutil_parser_isoparse(date_format, time_format, tz):
    # generate random date and time strings
    cur_date = datetime.date.today().strftime(date_format)
    cur_time = datetime.datetime.today().strftime(time_format)

    # include time zone if needed
    cur_time += 'Z' if tz else ''

    # concatenate date and time with T separator
    dt_str = f'{cur_date}T{cur_time}'

    assert isinstance(dateutil.parser.isoparse(dt_str), datetime.datetime)

# End program