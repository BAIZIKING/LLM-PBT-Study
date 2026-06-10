from hypothesis import given, strategies as st
import statistics

# Property 1: Mean within min/max range
@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1)) 
def test_mean_within_range(data):
    mean_value = statistics.mean(data)
    assert min(data) <= mean_value <= max(data)

# Property 2: Scaling data scales the mean
@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1), 
       st.floats(allow_nan=False, allow_infinity=False, exclude_min=True))
def test_mean_scaling(data, factor):
    scaled_data = [x * factor for x in data]
    assert statistics.mean(scaled_data) == statistics.mean(data) * factor 

# Property 3: Shifting data shifts the mean
@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1), 
       st.floats(allow_nan=False, allow_infinity=False))
def test_mean_shift(data, offset):
    shifted_data = [x + offset for x in data]
    assert statistics.mean(shifted_data) == statistics.mean(data) + offset

# Property 4: Identical values result in the same mean
@given(st.floats(allow_nan=False, allow_infinity=False))
def test_mean_identical_values(value):
    data = [value] * 10  # Create a list of identical values
    assert statistics.mean(data) == value

# Property 5: Mean is always a real number
@given(st.lists(st.one_of(st.floats(allow_nan=False), 
                         st.integers(), 
                         st.fractions()), min_size=1))
def test_mean_is_real(data):
    mean_value = statistics.mean(data)
    assert isinstance(mean_value, (int, float)) 
# End program