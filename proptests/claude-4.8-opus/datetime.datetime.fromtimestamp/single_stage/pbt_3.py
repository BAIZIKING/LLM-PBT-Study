from hypothesis import given, strategies as st
from datetime import datetime, timezone, timedelta

# Summary: Generate finite float timestamps within the safely-supported POSIX range
# (epoch through ~2038), and pick tz as either None (naive) or a timezone with
# various UTC offsets (aware). Check round-trip, naivety/awareness, type, and fold.
@given(st.data())
def test_datetime_datetime_fromtimestamp(data):
    timestamp = data.draw(
        st.floats(
            min_value=0,
            max_value=2**31 - 1,
            allow_nan=False,
            allow_infinity=False,
        )
    )
    tz = data.draw(
        st.sampled_from([
            None,
            timezone.utc,
            timezone(timedelta(hours=0)),
            timezone(timedelta(hours=5, minutes=30)),
            timezone(timedelta(hours=-8)),
            timezone(timedelta(hours=14)),
            timezone(timedelta(hours=-12)),
        ])
    )

    try:
        result = datetime.fromtimestamp(timestamp, tz)
    except (OverflowError, OSError, ValueError):
        # Documented: may raise OverflowError/OSError if out of platform range
        # or on localtime()/gmtime() failure.
        return

    # Property 3: result is always a datetime instance
    assert isinstance(result, datetime)

    # Property 4: fold must be 0 or 1
    assert result.fold in (0, 1)

    # Property 2: naivety vs. awareness based on tz
    if tz is None:
        assert result.tzinfo is None
    else:
        assert result.tzinfo is not None
        # The aware result's offset should match the requested tz offset
        assert result.utcoffset() == tz.utcoffset(result)

    # Property 1: round-trip — converting back to a timestamp should match.
    # For naive datetimes, .timestamp() assumes local time, which is consistent
    # with how fromtimestamp(None) interpreted it. For aware datetimes the
    # mapping is unambiguous (modulo sub-second float precision).
    recovered = result.timestamp()
    assert abs(recovered - timestamp) <= 1e-3
# End program