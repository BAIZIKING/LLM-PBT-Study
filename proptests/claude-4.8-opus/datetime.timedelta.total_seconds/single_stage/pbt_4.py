from hypothesis import given, strategies as st
from datetime import timedelta

# Summary: Generate arbitrary timedelta objects across the full valid range
# (including zero, negative, microsecond-scale, and extreme min/max values)
# using st.timedeltas(), then verify total_seconds() matches the documented
# division-form equivalence, returns a float, preserves sign, and reconstructs.
@given(st.data())
def test_datetime_timedelta_total_seconds(data):
    td = data.draw(st.timedeltas())

    result = td.total_seconds()

    # Property 1: documented equivalence to td / timedelta(seconds=1)
    assert result == td / timedelta(seconds=1)

    # Property 2: return type is float (per examples like 31536000.0)
    assert isinstance(result, float)

    # Property 3: sign consistency with the duration
    if td > timedelta(0):
        assert result > 0
    elif td < timedelta(0):
        assert result < 0
    else:
        assert result == 0.0

    # Property 4: reconstruction within microsecond tolerance for safe ranges
    # (docs note microsecond accuracy may be lost beyond ~270 years)
    if abs(td) < timedelta(days=270 * 365):
        reconstructed = timedelta(seconds=result)
        assert abs(reconstructed - td) <= timedelta(microseconds=1)
# End program