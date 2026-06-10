from hypothesis import given, strategies as st, assume
import datetime
import math

# Use a safe range of timestamps to avoid OverflowError/OSError on most platforms.
# Roughly years 1970 through 2038 are safest, but we allow a moderately wider range.
safe_timestamps = st.floats(
    min_value=0,
    max_value=2_000_000_000,  # ~ year 2033, safely within typical platform limits
    allow_nan=False,
    allow_infinity=False,
)

# A small selection of valid tzinfo instances.
tz_strategy = st.sampled_from([
    None,
    datetime.timezone.utc,
    datetime.timezone(datetime.timedelta(hours=5, minutes=30)),
    datetime.timezone(datetime.timedelta(hours=-8)),
    datetime.timezone(datetime.timedelta(hours=0)),
])


@given(st.data())
def test_datetime_datetime_fromtimestamp_property():
    ts = data.draw(safe_timestamps) if False else None  # placeholder, replaced below


# Property 1: The return value is always a datetime instance.
@given(ts=safe_timestamps, tz=tz_strategy)
def test_returns_datetime_instance(ts, tz):
    try:
        result = datetime.datetime.fromtimestamp(ts, tz)
    except (OverflowError, OSError):
        assume(False)
        return
    assert isinstance(result, datetime.datetime)


# Property 2: When tz is None, the returned datetime is naive.
@given(ts=safe_timestamps)
def test_naive_when_tz_none(ts):
    try:
        result = datetime.datetime.fromtimestamp(ts)
    except (OverflowError, OSError):
        assume(False)
        return
    assert result.tzinfo is None

    # Also test explicitly passing None.
    try:
        result2 = datetime.datetime.fromtimestamp(ts, None)
    except (OverflowError, OSError):
        assume(False)
        return
    assert result2.tzinfo is None


# Property 3: When tz is a valid tzinfo, the returned datetime is aware
# and its tzinfo corresponds to the provided tz.
@given(ts=safe_timestamps, tz=tz_strategy.filter(lambda t: t is not None))
def test_aware_when_tz_given(ts, tz):
    try:
        result = datetime.datetime.fromtimestamp(ts, tz)
    except (OverflowError, OSError):
        assume(False)
        return
    assert result.tzinfo is not None
    assert result.tzinfo is tz


# Property 4: Converting the result back to a timestamp yields the original timestamp.
@given(ts=safe_timestamps, tz=tz_strategy)
def test_roundtrip_timestamp(ts, tz):
    try:
        result = datetime.datetime.fromtimestamp(ts, tz)
    except (OverflowError, OSError):
        assume(False)
        return
    try:
        back = result.timestamp()
    except (OverflowError, OSError):
        assume(False)
        return
    # Allow for sub-second rounding/precision differences.
    assert math.isclose(back, ts, abs_tol=1e-3)


# Property 5: The fold attribute is always either 0 or 1.
@given(ts=safe_timestamps, tz=tz_strategy)
def test_fold_is_zero_or_one(ts, tz):
    try:
        result = datetime.datetime.fromtimestamp(ts, tz)
    except (OverflowError, OSError):
        assume(False)
        return
    assert result.fold in (0, 1)
# End program