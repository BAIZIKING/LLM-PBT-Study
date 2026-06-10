from hypothesis import given, strategies as st
import decimal

# Define a strategy for generating Decimal instances within a safe range
safe_decimals = st.decimals(
    min_value=-1e9, max_value=1e9, allow_nan=True, allow_infinity=False
)

@given(a=safe_decimals, b=safe_decimals)
def test_compare_is_decimal(a, b):
    """Output is always a Decimal instance."""
    result = a.compare(b)
    assert isinstance(result, decimal.Decimal)

@given(a=safe_decimals, b=safe_decimals)
def test_compare_output_values(a, b):
    """Output is always one of three specific values."""
    result = a.compare(b)
    assert result in [decimal.Decimal('-1'), decimal.Decimal('0'), decimal.Decimal('1')]

@given(a=st.floats(allow_nan=True), b=st.floats(allow_nan=True))
def test_compare_nan(a, b):
    """NaN inputs lead to NaN output."""
    a_dec = decimal.Decimal(str(a))
    b_dec = decimal.Decimal(str(b))
    result = a_dec.compare(b_dec)
    if math.isnan(a) or math.isnan(b):
        assert math.isnan(result)
    else:
        assert not math.isnan(result)

@given(a=safe_decimals, b=safe_decimals)
def test_compare_symmetry(a, b):
    """Symmetry for non-NaN inputs."""
    if not math.isnan(a) and not math.isnan(b):
        assert a.compare(b) == -b.compare(a)

@given(a=safe_decimals, b=safe_decimals, c=safe_decimals)
def test_compare_transitivity(a, b, c):
    """Transitivity for non-NaN inputs."""
    if not any(math.isnan(x) for x in [a, b, c]):
        comparison_ab = a.compare(b)
        comparison_bc = b.compare(c)
        comparison_ac = a.compare(c)
        if comparison_ab == 1 and comparison_bc == 1:
            assert comparison_ac == 1
        elif comparison_ab == -1 and comparison_bc == -1:
            assert comparison_ac == -1
        elif comparison_ab == 0 and comparison_bc == 0:
            assert comparison_ac == 0
# End program