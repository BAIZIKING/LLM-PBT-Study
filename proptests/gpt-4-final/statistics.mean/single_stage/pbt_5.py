from hypothesis import given, strategies as st
from statistics import mean
from fractions import Fraction
from decimal import Decimal

@given(st.data())
def test_mean(data):
    numerical_types = st.one_of(st.integers(), st.floats(allow_nan=False, allow_infinity=False), 
                                st.fractions(), st.decimals(allow_nan=False, allow_infinity=False))
    
    input_list = data.draw(st.lists(numerical_types, min_size=1))
    test_value = mean(input_list)
    
    # Property: The mean of a non-empty list of numbers should be of a numerical type.
    assert isinstance(test_value, (int, float, Fraction, Decimal))

    # Property: If all elements in the list are the same, the mean should be equal to any element.
    if len(set(input_list)) == 1:
        assert test_value == input_list[0]

    # Property: Adding a constant to all numbers in the list should add the constant to the mean.
    constant = data.draw(numerical_types)
    new_list = [x + constant for x in input_list]
    assert mean(new_list) == test_value + constant
