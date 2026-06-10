from hypothesis import given, strategies as st
import statistics
import math

# generate lists of floats for x and y with at least two elements and same length
xs_ys = st.tuples(st.lists(st.floats(allow_nan=False, allow_infinity=False, min_value=-1e10, max_value=1e10), min_size=2), 
                 st.lists(st.floats(allow_nan=False, allow_infinity=False, min_value=-1e10, max_value=1e10), min_size=2)).\
        filter(lambda x_y: len(x_y[0]) == len(x_y[1]))

@given(xs_ys)
def test_length_of_output(x_y):
    x, y = x_y
    output = statistics.linear_regression(x, y)
    assert len(output) == 2

@given(xs_ys)
def test_types_of_output(x_y):
    x, y = x_y
    output = statistics.linear_regression(x, y)
    assert isinstance(output[0], float)
    assert isinstance(output[1], float)

@given(xs_ys)
def test_consistency_of_function(x_y):
    x, y = x_y
    output1 = statistics.linear_regression(x, y)
    output2 = statistics.linear_regression(x, y)
    assert math.isclose(output1[0], output2[0], rel_tol=1e-9)
    assert math.isclose(output1[1], output2[1], rel_tol=1e-9)

@given(xs_ys)
def test_proportional_parameter_impact(x_y):
    x, y = x_y
    output = statistics.linear_regression(x, y, proportional=True)
    assert math.isclose(output[1], 0.0, abs_tol=1e-9)

@given(xs_ys)
def test_data_sufficiency(x_y):
    x, y = x_y
    output = statistics.linear_regression(x, y)
    assert output is not None

# End program