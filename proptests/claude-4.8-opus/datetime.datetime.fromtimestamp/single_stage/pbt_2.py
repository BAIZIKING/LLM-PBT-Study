from hypothesis import given, strategies as st
from datetime import datetime, timezone, timedelta

# Summary: Generate timestamps as finite floats in the portable range [0, 2**31)
# (years ~1970-2038) to avoid platform OverflowError/OSError, and pick tz as either
# None (naive) or a fixed-offset timezone (aware) with offsets in (-24h, +24h).
@given(st.data())
def test_datetime_datetime_fromtimestamp(data):
    timestamp = data.draw(
        st.floats(
            min_value=0,
            max_value=2**31 - 1,
            allow_nan=False,
            allow_infinity=False,
            allow_subnormal=False,
        )
    )
    tz = data.draw(
        st.one_of(
            st.none(),
            st.integers(min_value=-(24 * 60 - 1), max_value=24 * 60 - 1).map(
                lambda m: timezone(timedelta(minutes=m))
            ),
        )
    )

    result = datetime.fromtimestamp(timestamp, tz)

    # Property 1: result is always a datetime instance
    assert isinstance(result, datetime)

    # Property 2: naive vs aware depending on tz
    if tz is None:
        assert result.tzinfo is None
    else:
        assert result.tzinfo is not None
        assert result.tzinfo == tz

    # Property 4: fold must be 0 or 1
    assert result.fold in (0, 1)

    # Property 3: round-trip consistency within float tolerance
    recovered = result.timestamp()
    assert abs(recovered - timestamp) <= 1.0
# End program