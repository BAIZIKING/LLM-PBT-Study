from hypothesis import given, strategies as st
import datetime
import pytz

@given(st.integers(min_value=0, max_value=int(datetime.datetime(2038, 1, 19, 3, 14).timestamp())), st.sampled_from(list(pytz.all_timezones)))
def test_datetime_fromtimestamp(t, tz_str):
    tz = pytz.timezone(tz_str)
    dt = datetime.datetime.fromtimestamp(t, tz)
    # Property 1: Timezone Sensitivity
    t_utc = datetime.datetime.utcfromtimestamp(t)
    assert dt.astimezone(pytz.UTC) == t_utc

    # Property 2: Input-Output Equality
    t2 = dt.timestamp()
    assert abs(t - t2) < 1    # accounting for potential fractional seconds

    # Property 4: Contextual Sensitivity
    dt_naive = datetime.datetime.fromtimestamp(t)
    assert dt_naive.astimezone(pytz.UTC) != t_utc if dt.tzinfo is not None else True

    # Property 5: Leap Second Ignorance
    dt_plus_one = datetime.datetime.fromtimestamp(t+1, tz)
    assert (dt_plus_one - dt).total_seconds() == 1