from hypothesis import given, strategies as st
from datetime import timedelta
from fractions import Fraction

# Summary: Generate timedeltas from a mix of explicit edge cases, arbitrary normalized timedeltas, and non-normalized constructor components such as weeks, hours, minutes, seconds, milliseconds, and microseconds. This covers zero, positive and negative durations, sub-second values, normalization behavior, intervals around and beyond the documented 270-year precision boundary, and timedelta.min/timedelta.max. Check that total_seconds() is equivalent to division by timedelta(seconds=1), preserves sign, agrees with normalized reconstruction, and round-trips to exact microseconds for moderate-sized intervals where microsecond accuracy should be retained.
@given(st.data())
def test_datetime_timedelta_total_seconds(data):
    edge_cases = st.sampled_from(
        [
            timedelta(0),
            timedelta(microseconds=1),
            timedelta(microseconds=-1),
            timedelta(seconds=1),
            timedelta(seconds=-1),
            timedelta(days=1),
            timedelta(days=-1),
            timedelta(days=365),
            timedelta(weeks=40, days=84, hours=23, minutes=50, seconds=600),
            timedelta(days=270 * 365),
            timedelta(days=270 * 365 + 1),
            timedelta.min,
            timedelta.min + timedelta(microseconds=1),
            timedelta.max - timedelta(microseconds=1),
            timedelta.max,
        ]
    )

    arbitrary_timedeltas = st.timedeltas(
        min_value=timedelta.min,
        max_value=timedelta.max,
    )

    component_timedeltas = st.builds(
        lambda weeks, days, hours, minutes, seconds, milliseconds, microseconds: timedelta(
            weeks=weeks,
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            milliseconds=milliseconds,
            microseconds=microseconds,
        ),
        weeks=st.integers(-10_000, 10_000),
        days=st.integers(-200_000, 200_000),
        hours=st.integers(-1_000_000, 1_000_000),
        minutes=st.integers(-1_000_000, 1_000_000),
        seconds=st.integers(-1_000_000_000, 1_000_000_000),
        milliseconds=st.integers(-1_000_000_000, 1_000_000_000),
        microseconds=st.integers(-1_000_000_000_000, 1_000_000_000_000),
    )

    td = data.draw(st.one_of(edge_cases, arbitrary_timedeltas, component_timedeltas))

    result = td.total_seconds()

    assert isinstance(result, float)
    assert result == td / timedelta(seconds=1)

    normalized = timedelta(
        days=td.days,
        seconds=td.seconds,
        microseconds=td.microseconds,
    )
    assert normalized == td
    assert normalized.total_seconds() == result

    if td == timedelta(0):
        assert result == 0.0
    else:
        assert (result > 0) == (td > timedelta(0))

    total_microseconds = (
        (td.days * 24 * 60 * 60 + td.seconds) * 1_000_000
        + td.microseconds
    )

    if abs(td) <= timedelta(days=100 * 365):
        assert round(result * 1_000_000) == total_microseconds

    exact_seconds = Fraction(total_microseconds, 1_000_000)
    assert abs(Fraction.from_float(result) - exact_seconds) < Fraction(1, 1_000)

# End program