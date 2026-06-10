from hypothesis import given, strategies as st
from decimal import Decimal

# Summary: Generates diverse floats, integers, and edge cases to test Decimal.from_float.
@given(st.data())
def test_decimal_from_float(data):
    # Generate floats and integers, including NaN and infinities.
    float_value = data.draw(st.one_of(
        st.floats(allow_nan=True),
        st.integers(),
        st.just(float('inf')),
        st.just(float('-inf'))
    ))

    # Generate floats without NaN for value preservation checks.
    finite_float = data.draw(st.floats(allow_nan=False))

    # Test type consistency.
    result = Decimal.from_float(float_value)
    assert isinstance(result, Decimal)

    # Test value preservation for finite floats and integers.
    result = Decimal.from_float(finite_float)
    expected = Decimal(str(finite_float))
    assert result.almost_equal(expected)

    # Test NaN handling.
    nan_result = Decimal.from_float(float('nan'))
    assert nan_result.is_nan()

    # Test infinity handling.
    inf_result = Decimal.from_float(float('inf'))
    neg_inf_result = Decimal.from_float(float('-inf'))
    assert inf_result.is_infinite() and inf_result > 0
    assert neg_inf_result.is_infinite() and neg_inf_result < 0

# End program