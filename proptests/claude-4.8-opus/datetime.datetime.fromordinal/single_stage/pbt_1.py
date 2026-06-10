from hypothesis import given, strategies as st
from datetime import datetime

# Summary: Generate integer ordinals across the entire valid range
# [1, datetime.max.toordinal()] using st.integers, which naturally explores
# boundary values (1 and the max) as well as a wide variety of intermediate
# dates. Then verify type, zeroed time fields, absent tzinfo, and the
# round-trip correspondence between ordinal -> datetime -> ordinal.
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

    # Property 4: round-trip correspondence (ordinal -> datetime -> ordinal)
    assert result.toordinal() == ordinal

    # Property 5: ordinal 1 corresponds to January 1 of year 1
    if ordinal == 1:
        assert result.year == 1
        assert result.month == 1
        assert result.day == 1
# End program