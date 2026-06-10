from hypothesis import given, strategies as st
from datetime import datetime

# Summary: Generate integer ordinals within the valid documented range
# [1, datetime.max.toordinal()] to exercise lower/upper boundaries and
# random interior values; verify type, zeroed time fields, None tzinfo,
# and round-trip consistency with toordinal().
@given(st.data())
def test_datetime_datetime_fromordinal(data):
    ordinal = data.draw(
        st.integers(min_value=1, max_value=datetime.max.toordinal())
    )
    result = datetime.fromordinal(ordinal)

    # Property 1: result is a datetime instance
    assert isinstance(result, datetime)

    # Property 2: hour, minute, second, microsecond are all 0
    assert result.hour == 0
    assert result.minute == 0
    assert result.second == 0
    assert result.microsecond == 0

    # Property 3: tzinfo is None
    assert result.tzinfo is None

    # Property 4: round-trip consistency
    assert result.toordinal() == ordinal

    # Property 5: ordinal 1 maps to year 1, January 1
    if ordinal == 1:
        assert result.year == 1
        assert result.month == 1
        assert result.day == 1
# End program