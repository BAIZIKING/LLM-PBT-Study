from hypothesis import given, strategies as st
from datetime import timedelta

# Summary: Generate arbitrary timedeltas across the full valid range (including
# zero, negative, microsecond-precision, and extreme multi-century values) using
# st.timedeltas(). Verify total_seconds() equals the documented division form,
# returns a float, has a sign consistent with the duration, and (for non-extreme
# values) reconstructs an equivalent timedelta.
@given(st.data())
def test_datetime_timedelta_total_seconds(data):
    td = data.draw(st.timedeltas())
    result = td.total_seconds()

    # Property 2: result is always a float
    assert isinstance(result, float)

    # Property 1: equivalent to td / timedelta(seconds=1)
    assert result == td / timedelta(seconds=1)

    # Property 3: sign consistency with the duration
    if td > timedelta(0):
        assert result > 0
    elif td < timedelta(0):
        assert result < 0
    else:
        assert result == 0.0

    # Property 4: reconstruction for non-extreme values (within ~270 years),
    # where microsecond accuracy is preserved per the docs.
    if abs(td) < timedelta(days=270 * 365):
        reconstructed = timedelta(seconds=result)
        # Allow a tiny tolerance for float representation of microseconds.
        assert abs(reconstructed - td) <= timedelta(microseconds=1)
# End program