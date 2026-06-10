from hypothesis import given, strategies as st
from datetime import datetime

@given(st.integers(min_value=1, max_value=datetime.max.toordinal()))
def test_datetime_fromordinal(ordinal):
    date = datetime.fromordinal(ordinal)
    # Check that the generated date corresponds to the given ordinal
    assert date.toordinal() == ordinal
    # Check that the hour, minute, second, and microsecond are all 0,
    # and tzinfo is None
    assert date.hour == 0
    assert date.minute == 0
    assert date.second == 0
    assert date.microsecond == 0
    assert date.tzinfo is None
# End program