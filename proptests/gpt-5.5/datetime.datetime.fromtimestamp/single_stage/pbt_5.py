from hypothesis import given, strategies as st
from datetime import datetime, timezone, timedelta
import math

# Summary: Generate finite POSIX timestamps from a mix of common boundary values
# such as the epoch, fractional seconds, negative timestamps, 32-bit time_t edges,
# ordinary in-range dates, and very large finite values that may be unsupported by
# the platform. Also generate tz as either None, UTC, or a fixed-offset timezone.
# The test accepts the documented OverflowError/OSError for unsupported platform
# timestamps; otherwise it checks that the returned datetime has the documented
# naive/aware timezone behavior, has a valid fold value, and round-trips back to
# approximately the same timestamp after microsecond rounding.
@given(st.data())
def test_datetime_datetime_fromtimestamp(data):
    timestamp_strategy = st.one_of(
        st.sampled_from(
            [
                0,
                -0.0,
                1,
                -1,
                0.5,
                -0.5,
                0.999999,
                -0.999999,
                2_147_483_647,
                2_147_483_648,
                -2_147_483_648,
                4_102_444_800,   # around year 2100
                -2_208_988_800,  # around year 1900
                10**20,
                -(10**20),
            ]
        ),
        st.integers(min_value=-10**12, max_value=10**12),
        st.integers(min_value=-(2**63), max_value=2**63 - 1),
        st.floats(
            min_value=-10**12,
            max_value=10**12,
            allow_nan=False,
            allow_infinity=False,
            width=64,
        ),
        st.floats(
            allow_nan=False,
            allow_infinity=False,
            width=64,
        ),
    )

    timezone_strategy = st.one_of(
        st.none(),
        st.just(timezone.utc),
        st.integers(
            min_value=-(23 * 60 * 60 + 59 * 60 + 59),
            max_value=23 * 60 * 60 + 59 * 60 + 59,
        ).map(lambda seconds: timezone(timedelta(seconds=seconds))),
    )

    timestamp = data.draw(timestamp_strategy, label="timestamp")
    tz = data.draw(timezone_strategy, label="tz")

    try:
        result = datetime.fromtimestamp(timestamp, tz)
    except Exception as exc:
        assert isinstance(exc, (OverflowError, OSError))
        return

    assert isinstance(result, datetime)
    assert result.fold in (0, 1)

    if tz is None:
        assert result.tzinfo is None
    else:
        assert result.tzinfo is tz
        assert result.utcoffset() == tz.utcoffset(result)

    try:
        round_tripped_timestamp = result.timestamp()
    except (OverflowError, OSError):
        return

    assert math.isclose(
        round_tripped_timestamp,
        float(timestamp),
        rel_tol=1e-15,
        abs_tol=2e-6,
    )
# End program