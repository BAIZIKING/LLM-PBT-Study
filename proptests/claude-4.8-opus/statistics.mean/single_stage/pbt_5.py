from hypothesis import given, strategies as st
from statistics import mean
import math

# Summary: Generate non-empty lists of finite floats (with bounded magnitude to
# keep arithmetic stable). This covers single elements, repeated values, negatives,
# zeros, and varied magnitudes. We then check the core mathematical properties of
# mean: its definition (sum/len), its bounds (min <= mean <= max), the single-element
# identity, and translation invariance.
@given(st.data())
def test_statistics_mean():
    data = st.data  # placeholder to satisfy format; real draw below
    # (The decorator passes a `data` object; reassign via inner draw.)


@given(st.data())
def test_statistics_mean(data):
    values = data.draw(
        st.lists(
            st.floats(
                allow_nan=False,
                allow_infinity=False,
                min_value=-1e6,
                max_value=1e6,
            ),
            min_size=1,
            max_size=50,
        )
    )

    result = mean(values)
    n = len(values)
    tol = 1e-6 * max(1.0, abs(result), max(abs(v) for v in values))

    # Property 1: Definition -- mean equals sum divided by count.
    assert math.isclose(result, sum(values) / n, abs_tol=tol, rel_tol=1e-9)

    # Property 2: Bounds -- mean lies between min and max.
    assert min(values) - tol <= result <= max(values) + tol

    # Property 3: Single-element identity.
    if n == 1:
        assert math.isclose(result, values[0], abs_tol=tol, rel_tol=1e-9)

    # Property 4: Translation invariance -- shifting all values shifts the mean.
    c = data.draw(
        st.floats(allow_nan=False, allow_infinity=False,
                  min_value=-1e6, max_value=1e6)
    )
    shifted_mean = mean([v + c for v in values])
    shift_tol = 1e-6 * max(1.0, abs(shifted_mean), abs(result), abs(c))
    assert math.isclose(shifted_mean, result + c, abs_tol=shift_tol, rel_tol=1e-9)
# End program