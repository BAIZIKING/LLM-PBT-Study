from hypothesis import given, strategies as st
from decimal import Decimal, getcontext

# Decimal number strategy
decimal_strategy = st.decimals(min_value=-1e10, max_value=1e10, allow_nan=False, allow_infinity=False)

@given(decimal_strategy, decimal_strategy, decimal_strategy)
def test_fma_output_is_decimal(dec1, dec2, dec3):
    result = dec1.fma(dec2, dec3)
    assert isinstance(result, Decimal)

@given(decimal_strategy, decimal_strategy, decimal_strategy)
def test_fma_follows_equation(dec1, dec2, dec3):
    result = dec1.fma(dec2, dec3)
    assert result == (dec1 * dec2 + dec3)

@given(decimal_strategy, decimal_strategy, decimal_strategy)
def test_fma_does_not_change_inputs(dec1, dec2, dec3):
    dec1_copy, dec2_copy, dec3_copy = Decimal(dec1), Decimal(dec2), Decimal(dec3)
    _ = dec1.fma(dec2, dec3)
    assert dec1_copy == dec1 and dec2_copy == dec2 and dec3_copy == dec3

@given(decimal_strategy, decimal_strategy, decimal_strategy)
def test_fma_with_without_context(dec1, dec2, dec3):
    default_context = getcontext()
    alternate_context = getcontext()
    alternate_context.prec += 2
    result_default = dec1.fma(dec2, dec3, context=default_context)
    result_alternate = dec1.fma(dec2, dec3, context=alternate_context)
    assert result_default == result_alternate

@given(decimal_strategy, decimal_strategy, decimal_strategy)
def test_fma_no_rounding_intermediate(dec1, dec2, dec3):
    getcontext().prec += 3
    result_fma = dec1.fma(dec2, dec3)
    result_calc = (dec1 * dec2 + dec3)
    assert result_fma == result_calc
# End program