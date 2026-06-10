from hypothesis import given, strategies as st
from datetime import timedelta
import math

# Summary: Generate arbitrary timedelta objects via st.timedeltas(), drawn through
# st.data(). This covers zero, positive/negative, microsecond-scale, and very large
# (>270 year) durations. We verify the documented equivalence
# total_seconds() == td / timedelta(seconds=1), plus sign consistency between the
# duration and its computed total seconds.
@given(st.data())
def test_datetime_timedelta_total_seconds(data):
    td = data.draw(st.timedeltas())

    total = td.total_seconds()

    # Documented equivalence: total_seconds() == td / timedelta(seconds=1)
    quotient = td / timedelta(seconds=1)
    assert math.isclose(total, quotient, rel_tol=1e-9, abs_tol=0.0) or total == quotient

    # Sign consistency
    if td > timedelta(0):
        assert total > 0
    elif td < timedelta(0):
        assert total < 0
    else:
        assert total == 0.0
# End program