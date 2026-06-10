from hypothesis import given, strategies as st
import decimal

# Generates decimal numbers excluding NaN and +/- inf
valid_decimals = st.decimals(
    allow_nan=False, allow_infinity=False, min_value=-1e100, max_value=1e100)

@given(valid_decimals)
def test_output_type_property(decimal_number):
    n, d = decimal_number.as_integer_ratio()

    # Both n and d should be of type int
    assert isinstance(n, int)
    assert isinstance(d, int)

@given(valid_decimals)
def test_length_property(decimal_number):
    ratio = decimal_number.as_integer_ratio()

    # The length of ratio should be 2
    assert len(ratio) == 2

@given(valid_decimals)
def test_positive_denominator_property(decimal_number):
    n, d = decimal_number.as_integer_ratio()

    # d should be positive
    assert d > 0

@given(valid_decimals)
def test_exact_conversion_property(decimal_number):
    n, d = decimal_number.as_integer_ratio()
    
    # The original decimal should equal n/d
    assert abs(float(n)/d - float(decimal_number)) < 1e-10


@given(st.decimals(allow_nan=True, allow_infinity=True))
def test_exception_handling_property(decimal_number):
    if decimal_number.is_nan() or decimal_number.is_infinite():
        try:
            decimal_number.as_integer_ratio()
            assert False, "Exception expected but not raised."
        except (OverflowError, ValueError):
            pass
    else:
        try:
            decimal_number.as_integer_ratio()
        except (OverflowError, ValueError):
            assert False, "Unexpected exception raised."

# End program