from hypothesis import given, strategies as st
from datetime import datetime

# Summary: Generate unbounded integers via st.data().draw so values fall below,
# within, and above the valid range [1, datetime.max.toordinal()]. Assert ValueError
# for out-of-range inputs; for valid inputs verify the returned datetime has zeroed
# time fields, tzinfo None, and round-trips back to the original ordinal.
@given(st.data())
def test_datetime_datetime_fromordinal(data):
    ordinal = data.draw(st.integers())
    max_ordinal = datetime.max.toordinal()

    if ordinal < 1 or ordinal > max_ordinal:
        try:
            datetime.fromordinal(ordinal)
            assert False, f"Expected ValueError for out-of-range ordinal {ordinal}"
        except ValueError:
            pass
    else:
        result = datetime.fromordinal(ordinal)
        assert isinstance(result, datetime)
        assert result.hour == 0
        assert result.minute == 0
        assert result.second == 0
        assert result.microsecond == 0
        assert result.tzinfo is None
        assert result.toordinal() == ordinal
# End program