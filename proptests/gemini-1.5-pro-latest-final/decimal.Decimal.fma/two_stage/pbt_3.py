from hypothesis import given, strategies as st
import decimal

# Define a strategy for generating Decimal objects with limited precision and exponent
def decimal_strategy():
    return st.decimals(
        min_value=-1e10, max_value=1e10, allow_nan=True, allow_infinity=False
    )

@given(
    a=decimal_strategy(),
    b=decimal_strategy(),
    c=decimal_strategy(),
)
def test_decimal_Decimal_fma_property_1(a, b, c):
    fma_result = decimal.Decimal.fma(a, b, c)
    expected_result = a * b + c
    assert fma_result == expected_result

@given(
    a=decimal_strategy(),
    b=decimal_strategy(),
    c=decimal_strategy(),
)
def test_decimal_Decimal_fma_property_2(a, b, c):
    fma_result = decimal.Decimal.fma(a, b, c)
    assert isinstance(fma_result, decimal.Decimal)

@given(a=st.integers(), b=st.integers(), c=st.integers())
def test_decimal_Decimal_fma_property_3(a, b, c):
    fma_result = decimal.Decimal.fma(decimal.Decimal(a), decimal.Decimal(b), decimal.Decimal(c))
    assert fma_result.is_integer()

@given(
    a=st.one_of(
        st.decimals(allow_nan=True),
        st.floats(allow_nan=True),
    ),
    b=decimal_strategy(),
    c=decimal_strategy(),
)
def test_decimal_Decimal_fma_property_4(a, b, c):
    fma_result = decimal.Decimal.fma(a, b, c)
    if math.isnan(a):
        assert math.isnan(fma_result)

@given(b=decimal_strategy(), c=decimal_strategy())
def test_decimal_Decimal_fma_property_5(b, c):
    fma_result = decimal.Decimal.fma(decimal.Decimal(0), b, c)
    assert fma_result == c

# End program