from hypothesis import given, strategies as st
from fractions import Fraction
import statistics

# Summary: Generate non-empty lists of exact Fraction values (built from
# integer numerators/denominators covering zero, negatives, and large magnitudes).
# Using Fractions gives exact arithmetic so algebraic identities can be checked
# with strict equality. We verify: the sum/len definition, that the mean is
# bounded by min and max, the single-element identity, and translation invariance.
@given(st.data())
def test_statistics_mean(data):
    # Build a list of exact rational numbers
    fractions = data.draw(
        st.lists(
            st.builds(
                Fraction,
                st.integers(min_value=-10**9, max_value=10**9),
                st.integers(min_value=1, max_value=10**9),  # nonzero denominator
            ),
            min_size=1,
            max_size=50,
        )
    )

    result = statistics.mean(fractions)

    # Property 1: Definition — mean equals sum divided by count (exact with Fractions)
    expected = sum(fractions) / Fraction(len(fractions))
    assert result == expected

    # Property 2: Bounds — mean lies between min and max (central location)
    assert min(fractions) <= result <= max(fractions)

    # Property 3: Single-element list returns that element
    if len(fractions) == 1:
        assert result == fractions[0]

    # Property 4: Translation invariance — shifting all data by c shifts mean by c
    c = data.draw(st.builds(
        Fraction,
        st.integers(min_value=-10**6, max_value=10**6),
        st.integers(min_value=1, max_value=10**6),
    ))
    shifted = [x + c for x in fractions]
    assert statistics.mean(shifted) == result + c
# End program