from hypothesis import given, strategies as st
from statistics import mean, StatisticsError

# Generate a wide variety of numeric data types including ints, floats, 
# fractions, and decimals. Allow positive and negative values.
# Also generate empty sequences to test the empty input edge case.
# Use the recursive flag to generate lists of lists.
@given(st.one_of(
    st.lists(st.integers()), 
    st.lists(st.floats(allow_nan=False, allow_infinity=False)), 
    st.lists(st.fractions()),
    st.lists(st.decimals(allow_nan=False, allow_infinity=False)),
    st.lists(st.lists(st.one_of(
        st.integers(), st.floats(allow_nan=False, allow_infinity=False)), 
        min_size=1, max_size=10),
    ),
    st.lists(st.nothing(), max_size=0)
))
def test_statistics_mean(data):
    try:
        result = mean(data)
        
        # The result should be the sum divided by number of elements
        assert result == sum(data) / len(data)
        
        # The result should be greater than or equal to the minimum value 
        assert result >= min(data)
        
        # The result should be less than or equal to the maximum value
        assert result <= max(data)

    except StatisticsError:
        # StatisticsError should only be raised for an empty dataset
        assert len(data) == 0
        
    except TypeError:
        # TypeError should be raised if there is a type error
        # e.g. mean([1, 2, [3]]) or mean([1, "abc", 3]) 
        assert any(not isinstance(x, (int, float, complex, fraction, decimal)) for x in data)
# End program