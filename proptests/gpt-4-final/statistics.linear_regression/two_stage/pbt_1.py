from hypothesis import given, strategies as st
import statistics

# 1. Length of Output
@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2, max_size=10),
       st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2, max_size=10))
def test_linear_regression_output_length(x, y):
    if len(x) == len(y):
        slope, intercept = statistics.linear_regression(x, y)
        assert len((slope, intercept)) == 2

# 2. Type of Output
@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2, max_size=10),
       st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2, max_size=10))
def test_linear_regression_output_type(x, y):
    if len(x) == len(y):
        slope, intercept = statistics.linear_regression(x, y)
        assert isinstance(slope, (int, float))
        assert isinstance(intercept, (int, float))

# 3. Input Lengths
@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=10),
       st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=10))
def test_linear_regression_input_length(x, y):
    if len(x) != len(y):
        try:
            statistics.linear_regression(x, y)
            assert False, "Expected a Statistics Error due to unmatching input sizes"
        except statistics.StatisticsError:
            pass  # Expected Behavior

# 4. StatisticsError on Constant Independent Variable
@given(st.just([1.0]), st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2, max_size=10))
def test_linear_regression_on_constant_values(x, y):
  try:
      statistics.linear_regression(x, y)
      assert False, "Expected a Statistics Error due to constant x input"
  except statistics.StatisticsError:
      pass  # Expected Behavior

# 5. Intercept Value with Proportional Parameter
@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2, max_size=10),
       st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2, max_size=10))
def test_linear_regression_proportional_intercept(x, y):
    if len(x) == len(y):
        _, intercept = statistics.linear_regression(x, y, proportional=True)
        assert abs(intercept) < 1e-6  # Close to zero