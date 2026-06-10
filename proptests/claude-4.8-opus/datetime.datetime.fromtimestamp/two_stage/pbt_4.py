from hypothesis import given, strategies as st, assume
import datetime

# Use a conservative timestamp range to avoid OverflowError/OSError across platforms.
# Roughly the years 1970-2038 in seconds, which is commonly supported.
SAFE_MIN_TS = 0
SAFE_MAX_TS = 2_000_000_000  # ~ year 2033

timestamp_strategy = st.floats(
    min_value=SAFE_MIN_TS,
    max_value=SAFE_MAX_TS,
    allow_nan=False,
    allow_infinity=False,
)

tz_strategy = st.sampled_from([
    datetime.timezone.utc,
    datetime.timezone(datetime.timedelta(hours=5, minutes=30)),
    datetime.timezone(datetime.timedelta(hours=-8)),
    datetime.timezone(datetime.timedelta(hours=14)),
    datetime.timezone(datetime.timedelta(hours=-12)),
])


@given(st.data())
def test_datetime_datetime_fromtimestamp_returns_datetime_instance():
    # Property 1: result is always a datetime.datetime instance
    data = st.data
    pass


# Property 1: The return value is always an instance of datetime.datetime.
@given(ts=timestamp_strategy, tz=st.one_of(st.none(), tz_strategy))
def test_property_returns_datetime_instance(ts, tz):
    result = datetime.datetime.fromtimestamp(ts, tz)
    assert isinstance(result, datetime.datetime)


# Property 2: When tz is None, the returned datetime object is naive.
@given(ts=timestamp_strategy)
def test_property_naive_when_tz_none(ts):
    result = datetime.datetime.fromtimestamp(ts)
    assert result.tzinfo is None
    # Also test explicitly passing None
    result2 = datetime.datetime.fromtimestamp(ts, None)
    assert result2.tzinfo is None


# Property 3: When tz is not None, the result is aware and its tzinfo equals tz.
@given(ts=timestamp_strategy, tz=tz_strategy)
def test_property_aware_when_tz_given(ts, tz):
    result = datetime.datetime.fromtimestamp(ts, tz)
    assert result.tzinfo is not None
    assert result.tzinfo == tz


# Property 4: Round-trip via .timestamp() recovers the original timestamp.
@given(ts=timestamp_strategy, tz=tz_strategy)
def test_property_roundtrip_timestamp(ts, tz):
    result = datetime.datetime.fromtimestamp(ts, tz)
    recovered = result.timestamp()
    # Allow small tolerance for sub-second floating point representation.
    assert abs(recovered - ts) < 1e-3


# Property 5: Monotonicity - t1 < t2 implies fromtimestamp(t1) <= fromtimestamp(t2).
@given(t1=timestamp_strategy, t2=timestamp_strategy, tz=tz_strategy)
def test_property_monotonic(t1, t2, tz):
    assume(t1 < t2)
    d1 = datetime.datetime.fromtimestamp(t1, tz)
    d2 = datetime.datetime.fromtimestamp(t2, tz)
    assert d1 <= d2
# End program