from hypothesis import given, strategies as st
import statistics

# Property 1: Non-negative Output
@given(st.lists(st.floats(min_value=0, allow_nan=False, allow_infinity=False), min_size=1))
def test_geometric_mean_non_negative(data):
    result = statistics.geometric_mean(data)
    assert result >= 0

# Property 2: Scale Invariance
@given(st.lists(st.floats(min_value=0.001, allow_nan=False, allow_infinity=False), min_size=1), 
       st.floats(min_value=0.001, allow_nan=False, allow_infinity=False))
def test_geometric_mean_scale_invariance(data, factor):
    scaled_data = [x * factor for x in data]
    result1 = statistics.geometric_mean(data)
    result2 = statistics.geometric_mean(scaled_data)
    assert result2 == result1 * factor

# Property 3: Order Invariance
@given(st.lists(st.floats(min_value=0.001, allow_nan=False, allow_infinity=False), min_size=2, unique=True))
def test_geometric_mean_order_invariance(data):
    shuffled_data = data.copy()
    random.shuffle(shuffled_data)
    result1 = statistics.geometric_mean(data)
    result2 = statistics.geometric_mean(shuffled_data)
    assert result1 == result2

# Property 4: Relationship with Arithmetic Mean
@given(st.lists(st.floats(min_value=0, allow_nan=False, allow_infinity=False), min_size=1))
def test_geometric_mean_arithmetic_mean_relationship(data):
    geo_mean = statistics.geometric_mean(data)
    arith_mean = statistics.mean(data)
    assert geo_mean <= arith_mean

# Property 5: Value Range
@given(st.lists(st.floats(min_value=0.001, allow_nan=False, allow_infinity=False), min_size=1, unique=True))
def test_geometric_mean_value_range(data):
    geo_mean = statistics.geometric_mean(data)
    assert min(data) <= geo_mean <= max(data)

# End Program