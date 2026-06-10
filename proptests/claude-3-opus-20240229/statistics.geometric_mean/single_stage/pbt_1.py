from hypothesis import given, strategies as st
from statistics import geometric_mean, StatisticsError
import math

# Generate a variety of test cases including:
# - Non-empty sequences of positive floats
# - Sequences containing a zero which should raise StatisticsError 
# - Sequences containing a negative value which should raise StatisticsError
# - Empty sequence which should raise StatisticsError
# Check that:
# - Output is a float
# - Output equals the nth root of the product of all elements, where n is the number of elements
# - StatisticsError is raised for illegal inputs
@given(st.one_of(
    st.lists(st.floats(min_value=0.01, allow_infinity=False, allow_nan=False), min_size=1), 
    st.lists(st.floats(min_value=0.0, max_value=1e10, allow_infinity=False, allow_nan=False), min_size=1).map(lambda x: x + [0.0]),
    st.lists(st.floats(max_value=-0.01, allow_infinity=False, allow_nan=False), min_size=1),
    st.just([])
))
def test_geometric_mean(data):
    try:
        result = geometric_mean(data)
        assert isinstance(result, float)
        assert math.isclose(result, math.prod(data)**(1/len(data)))
    except StatisticsError:
        assert 0 in data or len(data) == 0 or any(x < 0 for x in data)
# End program