from hypothesis import given, strategies as st
from datetime import datetime, timezone, timedelta
import math

# Summary: Generate finite integer and float POSIX timestamps, emphasizing common
# boundary values such as the Unix epoch, negative timestamps, the 2038 boundary,
# and fractional seconds. Generate tz as either None or valid fixed-offset tzinfo
# instances, including UTC and near-extreme offsets. Check that successful calls
# return datetime instances with the documented naive/aware behavior, preserve
# tzinfo when supplied, expose a valid fold value, and round-trip back to the
# original timestamp within microsecond/float precision. Documented platform
# range failures, OverflowError and OSError, are accepted.
@given(st.data())
def test_datetime_datetime_fromtimestamp(data):
    timestamp_strategy = st.one_of(
        st.sampled_from([
            0,
            1,
            -1,
            0.0,
            0.5,
            -0.5,
            1_000_000_000,
            2_147_483_647,
            2_147_483_648,
            -2_147_483_648,
        ]),
        st.integers(min_value=-2_200_000_000, max_value=4_200_000_000),
        st.floats(
            min_value=-2_200_000_000,
            max_value=4_200_000_000,
            allow_nan=False,
            allow_infinity=False,
            width=64,
        ),
    )

    fixed_timezone_strategy = st.one_of(
        st.just(timezone.utc),
        st.builds(
            lambda minutes: timezone(timedelta(minutes=minutes)),
            st.integers(min_value=-23 * 60 - 59, max_value=23 * 60 + 59),
        ),
    )

    tz_strategy = st.one_of(st.none(), fixed_timezone_strategy)

    timestamp = data.draw(timestamp_strategy, label="timestamp")
    tz = data.draw(tz_strategy, label="tz")

    try:
        if tz is None:
            result = datetime.fromtimestamp(timestamp)
            explicit_none_result = datetime.fromtimestamp(timestamp, None)
            assert result == explicit_none_result
        else:
            result = datetime.fromtimestamp(timestamp, tz)
    except (OverflowError, OSError):
        return

    assert isinstance(result, datetime)
    assert result.fold in (0, 1)

    if tz is None:
        assert result.tzinfo is None
    else:
        assert result.tzinfo is tz

    round_tripped = result.timestamp()
    expected = float(timestamp)

    tolerance = max(1e-6, abs(expected) * 2**-52 * 8)
    assert math.isclose(round_tripped, expected, rel_tol=0.0, abs_tol=tolerance)
# End program