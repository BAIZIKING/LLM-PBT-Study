from hypothesis import given, strategies as st
import datetime
from dateutil import parser as dateutil_parser
from dateutil import tz

# Summary: Generate valid datetimes (naive and tz-aware, including UTC and
# arbitrary offsets), format them with isoformat() to produce guaranteed-valid
# ISO-8601 strings, and verify that isoparse round-trips back to an equal
# datetime, returns a datetime.datetime, and represents +00:00 offsets as tzutc.
@given(st.data())
def test_dateutil_parser_isoparse():
    data = st.data()
    # Choose whether to attach timezone info and which kind.
    tz_strategy = st.one_of(
        st.none(),
        st.just(tz.UTC),
        st.builds(
            tz.tzoffset,
            st.none(),
            st.integers(min_value=-86399, max_value=86399).map(
                # restrict to whole-minute offsets so isoformat -> isoparse is exact
                lambda s: (s // 60) * 60
            ),
        ),
    )
    dt = data.draw(
        st.datetimes(
            min_value=datetime.datetime(1, 1, 1, 0, 0, 0),
            max_value=datetime.datetime(9999, 12, 31, 23, 59, 59),
            timezones=tz_strategy,
        )
    )

    iso_str = dt.isoformat()
    result = dateutil_parser.isoparse(iso_str)

    # Property 1: result is a datetime.datetime
    assert isinstance(result, datetime.datetime)

    # Property 2: round-trip equality (compares instants for aware datetimes)
    assert result == dt

    # Property 3: a +00:00 (UTC-equivalent) offset must be represented as tzutc
    if dt.tzinfo is not None and dt.utcoffset() == datetime.timedelta(0):
        assert isinstance(result.tzinfo, tz.tzutc)
# End program