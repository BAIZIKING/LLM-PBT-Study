from hypothesis import given, strategies as st
from datetime import datetime, timezone, timedelta, tzinfo

# Summary: Generate safe-range POSIX timestamps as floats in [0, 2e9] (avoiding
# NaN/inf and platform overflow), paired with either None or a variety of fixed-offset
# timezones. Check return type, naive/aware semantics, valid fold, and round-trip via timestamp().
@given(st.data())
def test_datetime_datetime_fromtimestamp(data):
    timestamp = data.draw(
        st.floats(
            min_value=0,
            max_value=2_000_000_000,
            allow_nan=False,
            allow_infinity=False,
        )
    )
    tz = data.draw(
        st.one_of(
            st.none(),
            st.sampled_from([
                timezone.utc,
                timezone(timedelta(hours=0)),
                timezone(timedelta(hours=5, minutes=30)),
                timezone(timedelta(hours=-8)),
                timezone(timedelta(hours=14)),
                timezone(timedelta(hours=-12)),
            ]),
        )
    )

    result = datetime.fromtimestamp(timestamp, tz)

    # Property 1: result is always a datetime instance
    assert isinstance(result, datetime)

    # Property 2: naive vs aware semantics
    if tz is None:
        assert result.tzinfo is None
    else:
        assert isinstance(tz, tzinfo)
        assert result.tzinfo is tz

    # Property 3: fold is 0 or 1
    assert result.fold in (0, 1)

    # Property 4: round-trip consistency (within sub-second tolerance)
    # For aware datetimes, .timestamp() is unambiguous; for naive ones it uses local time.
    recovered = result.timestamp()
    assert abs(recovered - timestamp) <= 1.0
# End program