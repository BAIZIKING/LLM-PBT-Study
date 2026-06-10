from hypothesis import given, strategies as st
from datetime import timedelta

# Summary: Generate timedeltas from canonical fields and normalized constructor fields, mixing broad random ranges with edge cases such as zero, +/- one microsecond, +/- one second, year-sized durations, and timedelta min/max; check documented equivalence to division by one second and microsecond-preserving round trips for intervals safely below the documented precision-loss threshold.
@given(st.data())
def test_datetime_timedelta_total_seconds(data):
    edge_timedeltas = st.sampled_from([
        timedelta(0),
        timedelta(microseconds=1),
        timedelta(microseconds=-1),
        timedelta(seconds=1),
        timedelta(seconds=-1),
        timedelta(days=365),
        timedelta(days=-365),
        timedelta.max,
        timedelta.min,
    ])

    canonical_timedeltas = st.builds(
        timedelta,
        days=st.one_of(
            st.sampled_from([-999_999_999, -365 * 270, -1, 0, 1, 365 * 270, 999_999_999]),
            st.integers(min_value=-999_999_999, max_value=999_999_999),
        ),
        seconds=st.one_of(
            st.sampled_from([0, 1, 59, 60, 3599, 3600, 86399]),
            st.integers(min_value=0, max_value=86399),
        ),
        microseconds=st.one_of(
            st.sampled_from([0, 1, 999, 1000, 999999]),
            st.integers(min_value=0, max_value=999999),
        ),
    )

    normalized_constructor_timedeltas = st.builds(
        lambda weeks, days, hours, minutes, seconds, milliseconds, microseconds: timedelta(
            weeks=weeks,
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            milliseconds=milliseconds,
            microseconds=microseconds,
        ),
        weeks=st.integers(min_value=-10_000, max_value=10_000),
        days=st.integers(min_value=-10_000, max_value=10_000),
        hours=st.integers(min_value=-10_000, max_value=10_000),
        minutes=st.integers(min_value=-10_000, max_value=10_000),
        seconds=st.integers(min_value=-10_000, max_value=10_000),
        milliseconds=st.integers(min_value=-10_000, max_value=10_000),
        microseconds=st.integers(min_value=-10_000, max_value=10_000),
    )

    td = data.draw(
        st.one_of(edge_timedeltas, canonical_timedeltas, normalized_constructor_timedeltas)
    )

    total_seconds = td.total_seconds()

    assert isinstance(total_seconds, float)
    assert total_seconds == td / timedelta(seconds=1)

    if abs(td.days) <= 365 * 200:
        assert timedelta(seconds=total_seconds) == td
# End program