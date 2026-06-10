from hypothesis import given, strategies as st
from datetime import timedelta

# Summary: Generates a wide range of timedelta objects with varying days, seconds, and microseconds
@given(st.builds(timedelta, days=st.integers(), seconds=st.integers(0, 59), microseconds=st.integers(0, 999999)))
def test_timedelta_total_seconds(td):
    # Check equivalence to division by timedelta(seconds=1)
    assert td.total_seconds() == (td / timedelta(seconds=1))

    # Check sign preservation
    assert (td.total_seconds() >= 0) == (td >= timedelta(0))

    # Check microsecond accuracy for timedeltas within 270 years
    if abs(td.days) < 270 * 365:
        microseconds_expected = td.seconds * 1e6 + td.microseconds
        assert abs(td.total_seconds() * 1e6 - microseconds_expected) < 1e-6
# End program