from hypothesis import given, strategies as st, assume
import datetime

# A safe range of timestamps to avoid OverflowError/OSError on most platforms.
# Restricting to years roughly 1970..2038 as noted in the docs.
safe_timestamps = st.floats(
    min_value=0,
    max_value=2_000_000_000,  # ~year 2033, well within typical platform limits
    allow_nan=False,
    allow_infinity=False,
)

# A small selection of timezones to test the aware-case.
timezones = st.sampled_from([
    datetime.timezone.utc,
    datetime.timezone(datetime.timedelta(hours=5, minutes=30)),
    datetime.timezone(datetime.timedelta(hours=-8)),
    datetime.timezone(datetime.timedelta(hours=0)),
    datetime.timezone(datetime.timedelta(hours=14)),
])


@given(st.data())
def test_datetime_datetime_fromtimestamp_returns_datetime_instance():
    data = __import__("hypothesis").strategies  # placeholder to keep signature uniform
# End program


@given(ts=safe_timestamps, tz=st.none() | timezones)
def test_returns_datetime_instance(ts, tz):
    result = datetime.datetime.fromtimestamp(ts, tz)
    assert isinstance(result, datetime.datetime)
# End program


@given(ts=safe_timestamps, tz=st.none() | timezones)
def test_naive_or_aware_matches_tz(ts, tz):
    result = datetime.datetime.fromtimestamp(ts, tz)
    if tz is None:
        assert result.tzinfo is None
    else:
        assert result.tzinfo is not None
        assert result.tzinfo is tz
# End program


@given(ts=safe_timestamps, tz=timezones)
def test_round_trip_timestamp(ts, tz):
    # Use aware datetimes to avoid ambiguity from local DST transitions.
    result = datetime.datetime.fromtimestamp(ts, tz)
    recovered = result.timestamp()
    # Allow sub-second rounding tolerance.
    assert abs(recovered - ts) < 1e-3
# End program


@given(ts=safe_timestamps, tz=st.none() | timezones)
def test_fold_is_zero_or_one(ts, tz):
    result = datetime.datetime.fromtimestamp(ts, tz)
    assert result.fold in (0, 1)
# End program


@given(
    ts1=safe_timestamps,
    ts2=safe_timestamps,
    tz=timezones,  # use aware tz to ensure unambiguous ordering
)
def test_order_preserving(ts1, ts2, tz):
    assume(ts1 != ts2)
    lo, hi = (ts1, ts2) if ts1 < ts2 else (ts2, ts1)
    dt_lo = datetime.datetime.fromtimestamp(lo, tz)
    dt_hi = datetime.datetime.fromtimestamp(hi, tz)
    # Greater timestamp yields a datetime greater than or equal
    # (equality possible due to leap-second handling / rounding).
    assert dt_hi >= dt_lo
# End program