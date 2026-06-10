from hypothesis import given, strategies as st
import datetime

# Safe timestamp range (~1970..2033) to avoid platform OverflowError/OSError.
safe_timestamps = st.floats(
    min_value=0,
    max_value=2_000_000_000,
    allow_nan=False,
    allow_infinity=False,
)

# Fixed set of timezones, including None for the naive case.
timezones = st.sampled_from([
    None,
    datetime.timezone.utc,
    datetime.timezone(datetime.timedelta(hours=5)),
    datetime.timezone(datetime.timedelta(hours=-8)),
    datetime.timezone(datetime.timedelta(hours=0)),
])


@given(st.data())
def test_datetime_datetime_fromtimestamp_property(data):
    ts = data.draw(safe_timestamps)
    tz = data.draw(timezones)
    result = datetime.datetime.fromtimestamp(ts, tz)

    # Property 1: always returns a datetime.datetime instance.
    assert isinstance(result, datetime.datetime)

    # Property 2: tzinfo correctness depending on tz argument.
    if tz is None:
        assert result.tzinfo is None
    else:
        assert result.tzinfo is not None
        assert result.tzinfo == tz

    # Property 3: round-trip back to a timestamp ~ input (tolerance for fold/float).
    roundtrip = result.timestamp()
    assert abs(roundtrip - ts) <= 1.0 + 1e-6

    # Property 4: fold is always 0 or 1.
    assert result.fold in (0, 1)

    # Property 5: ordering preserved between two timestamps with the same tz.
    ts2 = data.draw(safe_timestamps)
    result2 = datetime.datetime.fromtimestamp(ts2, tz)
    if ts <= ts2:
        assert result <= result2
    else:
        assert result >= result2
# End program