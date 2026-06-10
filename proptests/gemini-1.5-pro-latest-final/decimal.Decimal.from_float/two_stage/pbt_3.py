from hypothesis import given, strategies as st
import decimal

# Define a strategy for generating floats, avoiding very large values
floats = st.floats(allow_nan=True, allow_infinity=True, width=32)

@given(floats)
def test_output_type(f):
    """Output is always a Decimal instance."""
    result = decimal.Decimal.from_float(f)
    assert isinstance(result, decimal.Decimal)

@given(floats)
def test_exact_representation(f):
    """Output is the exact decimal representation of the float."""
    result = decimal.Decimal.from_float(f)
    assert result == decimal.Decimal(str(f))

@given(st.floats(allow_nan=False, allow_infinity=False))  # Exclude NaN and inf
def test_sign_preservation(f):
    """Output has the same sign as the input float."""
    result = decimal.Decimal.from_float(f)
    assert (result > 0 and f > 0) or (result < 0 and f < 0) or (result == 0 and f == 0)

@given(floats)
def test_nan_infinity_handling(f):
    """NaN and infinities are handled correctly."""
    result = decimal.Decimal.from_float(f)
    if math.isnan(f):
        assert result.is_nan()
    elif math.isinf(f):
        if f > 0:
            assert result.is_infinite() and result > 0
        else:
            assert result.is_infinite() and result < 0

@given(floats)
def test_comparison_to_float(f):
    """Output is close to the original float within a small tolerance."""
    result = decimal.Decimal.from_float(f)
    assert abs(result - decimal.Decimal(str(f))) < 1e-15

# End program