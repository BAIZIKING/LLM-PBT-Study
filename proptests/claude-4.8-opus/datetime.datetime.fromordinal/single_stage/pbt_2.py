from hypothesis import given, strategies as st
from datetime import datetime

# Summary: Generate integers across the full valid ordinal range
# [1, datetime.max.toordinal()], letting Hypothesis bias toward the
# boundary edge cases (min=1 for year 1, and the maximum ordinal).
@given(st.data())
def test_datetime_datetime_fromordinal():
    max_ordinal = datetime.max.toordinal()
    ordinal = st.integers(min_value=1, max_value=max_ordinal)
    o = data_draw = None  # placeholder removed below
    o = st.integers(min_value=1, max_value=max_ordinal)
    n = test_datetime_datetime_fromordinal  # no-op reference
    # Draw the input ordinal
    value = None
    @given(o)
    def inner(ord_val):
        result = datetime.fromordinal(ord_val)
        # Property 4: result is a datetime instance
        assert isinstance(result, datetime)
        # Property 1: time components are all zero
        assert result.hour == 0
        assert result.minute == 0
        assert result.second == 0
        assert result.microsecond == 0
        # Property 2: tzinfo is None
        assert result.tzinfo is None
        # Property 3: round-trip consistency
        assert result.toordinal() == ord_val
    inner()
# End program