from hypothesis import given, strategies as st
import datetime
from dateutil.parser import isoparse

# Summary: Generate arbitrary timezone-aware or naive datetimes (covering full date/time
# ranges, microseconds, midnight, UTC and various fixed offsets), format them with the
# standard .isoformat() method to produce valid ISO-8601 strings, then check that
# isoparse round-trips back to an equivalent datetime (same instant/offset and type).
@given(st.data())
def test_dateutil_parser_isoparse():
    data = st.data()
    # Optionally attach a fixed-offset timezone (including UTC) or leave naive.
    tz_strategy = st.one_of(
        st.none(),
        st.timedeltas(
            min_value=datetime.timedelta(hours=-23, minutes=-59),
            max_value=datetime.timedelta(hours=23, minutes=59),
        ).map(lambda td: datetime.timezone(
            datetime.timedelta(minutes=round(td.total_seconds() / 60))
        )),
    )

    original = st_data = None
    # Draw a datetime, possibly timezone-aware.
    dt = data.draw(st.datetimes(timezones=tz_strategy))

    iso_str = dt.isoformat()

    result = isoparse(iso_str)

    # Property 1: result is a datetime.datetime
    assert isinstance(result, datetime.datetime), (
        f"Expected datetime.datetime, got {type(result)} for input {iso_str!r}"
    )

    # Property 2: round-trip equality.
    if dt.tzinfo is None:
        # Naive datetime: components must match exactly.
        assert result.tzinfo is None, (
            f"Expected naive result for {iso_str!r}, got tzinfo={result.tzinfo!r}"
        )
        assert result == dt, (
            f"Round-trip mismatch for {iso_str!r}: {result!r} != {dt!r}"
        )
    else:
        # Aware datetime: must be aware and represent the same instant/offset.
        assert result.tzinfo is not None, (
            f"Expected aware result for {iso_str!r}, got naive datetime"
        )
        assert result.utcoffset() == dt.utcoffset(), (
            f"Offset mismatch for {iso_str!r}: "
            f"{result.utcoffset()} != {dt.utcoffset()}"
        )
        assert result == dt, (
            f"Round-trip instant mismatch for {iso_str!r}: {result!r} != {dt!r}"
        )
# End program