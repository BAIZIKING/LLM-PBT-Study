from hypothesis import given, strategies as st
from datetime import datetime, timezone, tzinfo

# Summary: Generate POSIX timestamps as bounded, finite, non-NaN floats within the
# platform-safe range (epoch through ~year 2038) to avoid OverflowError/OSError, and
# generate tz as either None, a fixed-offset timezone, or a real IANA timezone. Then
# verify the result is a datetime with correct naive/aware status, a valid fold flag,
# and that it round-trips back to the original timestamp within tolerance.
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
        st.one_of(
            st.none(),
            st.timezones(),
            st.builds(timezone, st.timedeltas(
                min_value=-timezone.max.utcoffset(None) if False else __import__("datetime").timedelta(hours=-23),
                max_value=__import__("datetime").timedelta(hours=23),
            )),
        )
    )

    result = datetime.fromtimestamp(timestamp, tz)

    # Property 1: result must be a datetime instance
    assert isinstance(result, datetime)

    # Property 2: naive vs aware behavior
    if tz is None:
        assert result.tzinfo is None
    else:
        assert isinstance(tz, tzinfo)
        assert result.tzinfo is tz

    # Property 4: fold must be 0 or 1
    assert result.fold in (0, 1)

    # Property 3: round-trip consistency (allow tolerance for float/microsecond rounding)
    recovered = result.timestamp()
    assert abs(recovered - timestamp) <= 1e-3
# End program