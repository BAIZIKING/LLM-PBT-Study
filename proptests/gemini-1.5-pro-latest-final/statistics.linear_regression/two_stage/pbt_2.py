from hypothesis import given, strategies as st
import statistics

# Define strategies for generating well-behaved numeric data
finite_floats = st.floats(allow_nan=False, allow_infinity=False)

# 1. Output Type
@given(x=st.lists(finite_floats, min_size=2), y=st.lists(finite_floats, min_size=2))
def test_linear_regression_output_type(x, y):
    result = statistics.linear_regression(x, y)
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert all(isinstance(value, float) for value in result)

# 2. Slope Sign
@given(x=st.lists(finite_floats, min_size=2, unique=True), 
       y=st.lists(finite_floats, min_size=2))
def test_linear_regression_slope_sign(x, y):
    slope, _ = statistics.linear_regression(x, y)
    correlation = statistics.correlation(x, y)
    if correlation > 0:
        assert slope >= 0
    elif correlation < 0:
        assert slope <= 0

# 3. Proportional Intercept
@given(x=st.lists(finite_floats, min_size=2), y=st.lists(finite_floats, min_size=2))
def test_linear_regression_proportional_intercept(x, y):
    _, intercept = statistics.linear_regression(x, y, proportional=True)
    assert intercept == 0.0

# 4. Data Order Invariance
@given(x=st.lists(finite_floats, min_size=2), y=st.lists(finite_floats, min_size=2))
def test_linear_regression_order_invariance(x, y):
    result1 = statistics.linear_regression(x, y)
    result2 = statistics.linear_regression(list(reversed(x)), list(reversed(y)))
    assert result1 == result2

# 5. Translation Invariance
@given(x=st.lists(finite_floats, min_size=2), 
       y=st.lists(finite_floats, min_size=2),
       offset=finite_floats)
def test_linear_regression_translation_invariance(x, y, offset):
    slope1, intercept1 = statistics.linear_regression(x, y)
    slope2, intercept2 = statistics.linear_regression([v + offset for v in x], [v + offset for v in y])
    assert slope1 == slope2
    assert intercept2 == intercept1 + offset
# End program