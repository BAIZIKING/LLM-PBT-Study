from hypothesis import given, strategies as st, assume
from datetime import datetime, timezone, timedelta

# Summary: Generate timestamps as ints/floats within a safe, broad range
# (including epoch 0, negatives, and fractional seconds) and a tz that is
# either None, UTC, fixed offsets, or a zoneinfo timezone. We then verify
# type/naivety, fold validity, aware-ness, and round-trip via .timestamp().
@given(st.data())
def test_datetime_datetime_fromtimestamp(data):
    # Conservative range to avoid platform OverflowError/OSError
    # (~ year 1900 to year 2100 in seconds since epoch)
    safe_min = -2208988800.0
    safe_max = 4102444800.0

    timestamp = data.draw(
        st.one_of(
            st.integers(min_value=int(safe_min), max_value=int(safe_max)),
            st.floats(
                min_value=safe_min,
                max_value=safe_max,
                allow_nan=False,
                allow_infinity=False,
            ),
        )
    )

    tz_strategy = st.one_of(
        st.none(),
        st.just(timezone.utc),
        st.integers(min_value=-23, max_value=23).map(
            lambda h: timezone(timedelta(hours=h))
        ),
        st.timezones(),  # zoneinfo-based timezones
    )
    tz = data.draw(tz_strategy)

    try:
        result = datetime.fromtimestamp(timestamp, tz)
    except (OverflowError, OSError, ValueError):
        # Documented: platform may raise OverflowError/OSError out of range.
        assume(False)
        return

    # Property 1: result is a datetime
    assert isinstance(result, datetime)

    # Property 2: naivety / awareness based on tz
    if tz is None:
        assert result.tzinfo is None
    else:
        assert result.tzinfo is not None
        # Aware results must have a defined utcoffset
        assert result.utcoffset() is not None

    # Property 3: fold is always 0 or 1
    assert result.fold in (0, 1)

    # Property 4: round-trip via .timestamp() recovers the input.
    # For naive datetimes near DST transitions this can be ambiguous;
    # skip folded results to avoid known platform ambiguity.
    assume(result.fold == 0)
    recovered = result.timestamp()
    # Sub-second precision tolerance; .timestamp() uses microsecond resolution.
    assert abs(recovered - float(timestamp)) <= 1e-3
# End program