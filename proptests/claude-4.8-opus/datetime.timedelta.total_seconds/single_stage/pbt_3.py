from datetime import timedelta
from hypothesis import given, strategies as st

# Summary: Generate timedelta objects constrained to within ~270 years (to avoid
# documented microsecond-accuracy loss), covering zero, negative, positive, tiny,
# and large durations. Verify total_seconds() equals td / timedelta(seconds=1),
# matches the component-based computation, and is sign-consistent.
@given(st.data())
def test_datetime_timedelta_total_seconds(data):
    # Constrain to ~270 years to stay within exact microsecond accuracy
    bound = timedelta(days=270 * 365)
    td = data.draw(st.timedeltas(min_value=-bound, max_value=bound))

    result = td.total_seconds()

    # Property 1: Equivalent to td / timedelta(seconds=1) (documented equivalence)
    assert result == td / timedelta(seconds=1)

    # Property 2: Consistent with the timedelta's components
    expected = td.days * 86400 + td.seconds + td.microseconds / 1_000_000
    assert result == expected

    # Property 3: Sign consistency
    if td > timedelta(0):
        assert result > 0
    elif td < timedelta(0):
        assert result < 0
    else:
        assert result == 0.0
# End program