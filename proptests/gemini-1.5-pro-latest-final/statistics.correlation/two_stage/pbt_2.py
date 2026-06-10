from hypothesis import given, strategies as st
import statistics

# Define strategies for generating lists of numbers
list_strategy = st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2) 

@given(x=list_strategy, y=list_strategy)
def test_correlation_range(x, y):
    """Output Range: Correlation coefficient should be between -1 and 1."""
    result = statistics.correlation(x, y)
    assert -1 <= result <= 1

@given(x=list_strategy, y=list_strategy)
def test_correlation_symmetry(x, y):
    """Symmetry: Order of inputs should not affect the result."""
    result1 = statistics.correlation(x, y)
    result2 = statistics.correlation(y, x)
    assert result1 == result2

@given(x=st.floats(allow_nan=False, allow_infinity=False), y=st.floats(allow_nan=False, allow_infinity=False))
def test_correlation_constant_input(x, y):
    """Constant Input: Correlation of constant lists should be NaN."""
    constant_list = [x] * 10
    result = statistics.correlation(constant_list, constant_list)
    assert math.isnan(result)

@given(x=list_strategy, y=list_strategy)
def test_correlation_monotonic_transformation(x, y):
    """Monotonic Transformation: Applying a monotonic function should not change the result."""
    def monotonic_function(z):
        return z * 2 + 10  # Example monotonic function

    transformed_x = [monotonic_function(val) for val in x]
    transformed_y = [monotonic_function(val) for val in y]
    result1 = statistics.correlation(x, y)
    result2 = statistics.correlation(transformed_x, transformed_y)
    assert result1 == result2

@given(x=list_strategy, y=list_strategy)
def test_correlation_reverse_order(x, y):
    """Reverse Order: Reversing order of elements should not change the result."""
    result1 = statistics.correlation(x, y)
    result2 = statistics.correlation(list(reversed(x)), list(reversed(y)))
    assert result1 == result2
# End program 