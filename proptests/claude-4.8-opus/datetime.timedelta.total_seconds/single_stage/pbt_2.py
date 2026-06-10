from hypothesis import given, strategies as st
from datetime import timedelta

# Summary: Generate arbitrary timedelta objects across the full valid range
# (including zero, negatives, microsecond precision, and min/max boundaries)
# using st.timedeltas(), then verify total_seconds() matches its documented
# definition (td / timedelta(seconds=1)), returns a float, and is sign-consistent.
@given(st.data())
def test_datetime_timedelta_total_seconds():
    data = st.data()
    td = data.draw(st.timedeltas())

    result = td.total_seconds()

    # Property 1: Equivalent to division by timedelta(seconds=1)
    assert result == td / timedelta(seconds=1)

    # Property 2: Result is always a float
    assert isinstance(result, float)

    # Property 3: Sign consistency with the duration
    if td > timedelta(0):
        assert result > 0
    elif td < timedelta(0):
        assert result < 0
    else:
        assert result == 0.0
# End program