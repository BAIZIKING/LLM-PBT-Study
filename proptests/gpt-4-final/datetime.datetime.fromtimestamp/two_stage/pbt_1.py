from hypothesis import given, strategies as st
import datetime

# Property 1: Date and time accuracy
@given(st.integers(min_value=0, max_value=int(datetime.datetime(2038,1,1).timestamp())))
def test_datetime_accuracy(ts):
    dt = datetime.datetime.fromtimestamp(ts)
    assert dt.timestamp() == ts

# Property 2: Timezone handling
@given(st.integers(min_value=0, max_value=int(datetime.datetime(2038,1,1).timestamp())), st.sampled_from([datetime.timezone.utc, None]))
def test_datetime_timezone(ts, tz):
    dt = datetime.datetime.fromtimestamp(ts, tz)
    if tz is None:
        assert dt.tzinfo is None
    else:
        assert dt.tzinfo == tz

# Property 3: Error handling
@given(st.integers(min_value=int(datetime.datetime(2038,1,1).timestamp())))
def test_datetime_overflow(ts):
    try:
        dt = datetime.datetime.fromtimestamp(ts)
    except OverflowError:
        pass

# Property 4: Handling of naive datetime objects
@given(st.integers(min_value=0, max_value=int(datetime.datetime(2038,1,1).timestamp())))
def test_datetime_naive(ts):
    dt = datetime.datetime.fromtimestamp(ts)
    assert dt.tzinfo is None

# Property 5: fold attribute
@given(st.integers(min_value=0), st.sampled_from([0, 1]))
def test_datetime_fold(ts, fold):
    dt = datetime.datetime.fromtimestamp(ts)
    assert dt.fold in [0, 1]
# End program