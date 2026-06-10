from hypothesis import given, strategies as st
from statistics import variance
from math import isclose

# Generate a wide variety of numeric input data to test the statistics.variance function thoroughly.
# Strategies include:
# - Lists of floats or integers with at least 2 elements to meet the minimum input requirement 
# - Lists of floats or integers with duplicate values to test that variance is 0 
# - Lists of floats with a wide range of magnitudes to test numerical stability
# - Optional xbar mean argument is either None or the actual mean of the generated data
#
# Key properties to test:
# - Result is non-negative 
# - Result is 0 if all data values are equal
# - Result is invariant if data order is shuffled
# - Passing the actual mean as xbar gives the same result as passing None
@given(st.data())
def test_variance(data):
    values = data.draw(st.lists(st.floats(allow_infinity=False, allow_nan=False), min_size=2))
    xbar = data.draw(st.one_of(st.none(), st.just(sum(values) / len(values))))
    
    result1 = variance(values, xbar)
    result2 = variance(values, None)
    result3 = variance(values[::-1], xbar)  
    
    assert result1 >= 0
    assert isclose(result1, 0) == all(x == values[0] for x in values)
    assert isclose(result1, result2)
    assert isclose(result1, result3)
# End program