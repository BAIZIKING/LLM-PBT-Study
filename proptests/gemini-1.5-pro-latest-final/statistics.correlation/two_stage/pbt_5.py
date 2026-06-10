from hypothesis import given, strategies as st
import statistics

# Define strategies for generating lists of numbers
list_strategy = st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2)

@given(list_strategy, list_strategy)
def test_correlation_range(x, y):
    # Property 1: Output Range
    result = statistics.correlation(x, y)
    assert -1.0 <= result <= 1.0

@given(list_strategy, list_strategy)
def test_correlation_symmetry(x, y):
    # Property 2: Symmetry
    result_xy = statistics.correlation(x, y)
    result_yx = statistics.correlation(y, x)
    assert result_xy == result_yx

@given(st.floats(allow_nan=False, allow_infinity=False))
def test_correlation_constant_input(value):
    # Property 3: Constant Input
    constant_list = [value] * 5  # Create a list with identical values
    result_linear = statistics.correlation(constant_list, constant_list)
    result_ranked = statistics.correlation(constant_list, constant_list, method='ranked')
    assert math.isnan(result_linear) 
    assert result_ranked == 0.0

@given(list_strategy, list_strategy)
def test_correlation_ranked_monotonicity(x, y):
    # Property 4: Monotonicity with Respect to Ranking (Ranked Method)
    import numpy as np
    # Sort both lists in the same way, maintaining relative order
    x_sorted, y_sorted = zip(*sorted(zip(x, y)))
    result_original = statistics.correlation(x, y, method='ranked')
    result_sorted = statistics.correlation(x_sorted, y_sorted, method='ranked')
    assert result_original == result_sorted

@given(list_strategy, list_strategy)
def test_correlation_outlier_effect(x, y):
    # Property 5: Effect of Outliers (Linear Method)
    import copy
    x_outlier = copy.deepcopy(x)
    y_outlier = copy.deepcopy(y)
    x_outlier.append(x_outlier[-1] * 100)  # Add outlier
    y_outlier.append(y_outlier[-1] * 100)  # Add outlier

    result_original = statistics.correlation(x, y)
    result_outlier = statistics.correlation(x_outlier, y_outlier)
    # Assert that the difference is significant (e.g., greater than 0.1)
    assert abs(result_original - result_outlier) > 0.1
# End program