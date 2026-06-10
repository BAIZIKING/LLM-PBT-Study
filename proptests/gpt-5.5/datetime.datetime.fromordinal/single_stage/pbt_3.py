from hypothesis import given, strategies as st
from datetime import datetime, date

# Summary: Generate ordinals from a mix of boundary-focused values and broad integers:
# valid ordinals in [1, datetime.max.toordinal()], edge cases around the lower and
# upper bounds, and invalid integers outside the allowed range. For valid ordinals,
# check that the returned datetime has the same ordinal, midnight time fields, and
# tzinfo is None. For invalid ordinals, check that ValueError is raised.
@given(st.data())
def test_datetime_datetime_fromordinal(data):
    max_ordinal = datetime.max.toordinal()

    ordinal = data.draw(
        st.one_of(
            st.sampled_from([
                -10,
                -1,
                0,
                1,
                2,
                max_ordinal - 1,
                max_ordinal,
                max_ordinal + 1,
                max_ordinal + 10,
            ]),
            st.integers(min_value=-10_000, max_value=max_ordinal + 10_000),
        )
    )

    if 1 <= ordinal <= max_ordinal:
        result = datetime.fromordinal(ordinal)

        assert isinstance(result, datetime)
        assert result.toordinal() == ordinal
        assert result.date() == date.fromordinal(ordinal)
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