from hypothesis import given, strategies as st
from datetime import datetime

MAX_ORDINAL = datetime.max.toordinal()

# Summary: Generate valid ordinals across the full supported range, explicit boundary values near 1 and datetime.max.toordinal(), and invalid integers just outside the range and farther away. For valid ordinals, check round-tripping, midnight time fields, and naive tzinfo; for invalid ordinals, check that ValueError is raised.
@given(st.data())
def test_datetime_datetime_fromordinal(data):
    ordinal = data.draw(
        st.one_of(
            st.integers(min_value=1, max_value=MAX_ORDINAL),
            st.sampled_from([
                1,
                2,
                3,
                MAX_ORDINAL - 2,
                MAX_ORDINAL - 1,
                MAX_ORDINAL,
            ]),
            st.integers(min_value=-1_000_000_000, max_value=0),
            st.integers(min_value=MAX_ORDINAL + 1, max_value=1_000_000_000),
        )
    )

    if 1 <= ordinal <= MAX_ORDINAL:
        result = datetime.fromordinal(ordinal)

        assert isinstance(result, datetime)
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