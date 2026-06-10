from hypothesis import given, strategies as st
from datetime import datetime

# Summary: Generate ordinals from a mix of valid values, invalid values, and boundary cases:
# 0, 1, datetime.max.toordinal(), values just outside the valid range, and very large/small integers.
# Properties checked: valid ordinals round-trip via toordinal(), produce midnight time fields,
# and have tzinfo=None; invalid ordinals raise ValueError.
@given(st.data())
def test_datetime_datetime_fromordinal(data):
    max_ordinal = datetime.max.toordinal()

    ordinal = data.draw(
        st.one_of(
            st.sampled_from([
                -10**100,
                -1,
                0,
                1,
                2,
                max_ordinal - 1,
                max_ordinal,
                max_ordinal + 1,
                10**100,
            ]),
            st.integers(min_value=1, max_value=max_ordinal),
            st.integers(max_value=0),
            st.integers(min_value=max_ordinal + 1),
        )
    )

    if 1 <= ordinal <= max_ordinal:
        result = datetime.fromordinal(ordinal)

        assert result.toordinal() == ordinal
        assert result.hour == 0
        assert result.minute == 0
        assert result.second == 0
        assert result.microsecond == 0
        assert result.tzinfo is None
    else:
        try:
            datetime.fromordinal(ordinal)
        except ValueError:
            pass
        else:
            raise AssertionError("datetime.fromordinal() should raise ValueError for invalid ordinal")
# End program