from hypothesis import given, strategies as st
from datetime import datetime
import pytest

# Summary: Generate integers both inside the valid ordinal range [1, datetime.max.toordinal()]
# (including boundary edge cases) and outside it (<=0 or > max), to verify correct datetime
# construction (zeroed time, None tzinfo, round-trip) for valid inputs and ValueError otherwise.
@given(st.data())
def test_datetime_datetime_fromordinal(data):
    max_ordinal = datetime.max.toordinal()
    ordinal = data.draw(st.one_of(
        st.integers(min_value=1, max_value=max_ordinal),          # valid range
        st.integers(min_value=-1000, max_value=0),                # invalid low
        st.integers(min_value=max_ordinal + 1, max_value=max_ordinal + 1000),  # invalid high
    ))

    if 1 <= ordinal <= max_ordinal:
        result = datetime.fromordinal(ordinal)
        # Time components must all be zero
        assert result.hour == 0
        assert result.minute == 0
        assert result.second == 0
        assert result.microsecond == 0
        # tzinfo must be None
        assert result.tzinfo is None
        # Round-trip consistency
        assert result.toordinal() == ordinal
    else:
        with pytest.raises(ValueError):
            datetime.fromordinal(ordinal)
# End program