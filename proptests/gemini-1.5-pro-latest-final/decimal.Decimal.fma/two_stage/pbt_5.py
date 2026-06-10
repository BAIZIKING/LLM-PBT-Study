from hypothesis import given, strategies as st
import decimal

# Property 1: Output equivalence to manual computation.
@given(st.decimals(allow_nan=False, allow_infinity=False),
       st.decimals(allow_nan=False, allow_infinity=False),
       st.decimals(allow_nan=False, allow_infinity=False))
def test_decimal_Decimal_fma_equivalence_to_multiplication_and_addition(a, b, c):
    assert decimal.Decimal.fma(a, b, c) == a * b + c

# Property 2: Integer inputs yield integer outputs.
@given(st.integers(), st.integers(), st.integers())
def test_decimal_Decimal_fma_integer_inputs_yield_integer_output(a, b, c):
    result = decimal.Decimal.fma(decimal.Decimal(a), decimal.Decimal(b), decimal.Decimal(c))
    assert result == int(result)

# Property 3: Positive inputs yield positive output.
@given(st.decimals(min_value=0, allow_nan=False, allow_infinity=False),
       st.decimals(min_value=0, allow_nan=False, allow_infinity=False),
       st.decimals(min_value=0, allow_nan=False, allow_infinity=False))
def test_decimal_Decimal_fma_positive_inputs_yield_positive_output(a, b, c):
    assert decimal.Decimal.fma(a, b, c) > 0

# Property 4: Negative inputs yield negative output.
@given(st.decimals(max_value=0, allow_nan=False, allow_infinity=False),
       st.decimals(max_value=0, allow_nan=False, allow_infinity=False),
       st.decimals(max_value=0, allow_nan=False, allow_infinity=False))
def test_decimal_Decimal_fma_negative_inputs_yield_negative_output(a, b, c):
    assert decimal.Decimal.fma(a, b, c) < 0

# Property 5: Commutativity of inputs a and b under multiplication.
@given(st.decimals(allow_nan=False, allow_infinity=False),
       st.decimals(allow_nan=False, allow_infinity=False),
       st.decimals(allow_nan=False, allow_infinity=False))
def test_decimal_Decimal_fma_commutativity_of_multiplication(a, b, c):
    result1 = decimal.Decimal.fma(a, b, c)
    result2 = decimal.Decimal.fma(b, a, c)
    assert result1 == result2
# End program