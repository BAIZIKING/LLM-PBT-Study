from datetime import datetime
from hypothesis import given, strategies as st

_MAX_ORDINAL = datetime.max.toordinal()

# Summary: Generate ordinals from a mix of the full valid range, values near 1,
# values near datetime.max.toordinal(), and invalid values just outside both
# bounds. For valid ordinals, check that fromordinal round-trips through
# toordinal(), has zero time fields, and has tzinfo=None. For invalid ordinals,
# check that ValueError is raised.
@given(st.data())
def test_datetime_datetime_fromordinal(data):
    ordinal = data.draw(
        st.one_of(
            st.integers(min_value=1, max_value=_MAX_ORDINAL),
            st.integers(min_value=-10, max_value=10),
            st.integers(min_value=_MAX_ORDINAL - 10, max_value=_MAX_ORDINAL + 10),
            st.sampled_from(
                [
                    0,
                    1,
                    2,
                    _MAX_ORDINAL - 1,
                    _MAX_ORDINAL,
                    _MAX_ORDINAL + 1,
                ]
            ),
        ),
        label="ordinal",
    )

    if 1 <= ordinal <= _MAX_ORDINAL:
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
            raise AssertionError("datetime.fromordinal() should raise ValueError")

# End program