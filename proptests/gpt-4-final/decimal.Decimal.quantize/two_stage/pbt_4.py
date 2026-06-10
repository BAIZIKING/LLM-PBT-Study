from hypothesis import given, strategies as st
from decimal import Decimal, getcontext, InvalidOperation

# Property 1: Output should have same exponent as the second operand
@given(st.floats(allow_nan=False, allow_infinity=False), st.integers())
def test_exponent(first_num, second_exp):
    second_num = Decimal(10 ** second_exp)
    result = Decimal(first_num).quantize(second_num)
    assert result.as_tuple().exponent == second_num.as_tuple().exponent

# Property 2: If output coefficient length exceeds `precision`, raises InvalidOperation
@given(st.floats(allow_nan=False, allow_infinity=False), st.integers(min_value=-28, max_value=28), st.integers(min_value=1, max_value=28))
def test_precision(first_num, second_exp, precision):
    second_num = Decimal(10 ** second_exp)
    getcontext().prec = precision
    try:
        result = Decimal(first_num).quantize(second_num)
        assert len(str(result).split('.')[1]) <= precision
    except InvalidOperation:
        assert len(str(first_num).split('.')[1]) > precision

# Property 3: Even with potentially subnormal and inexact results, no Underflow signaled
@given(st.floats(min_value=0, max_value=0), st.floats(allow_nan=False, allow_infinity=False))
def test_subnormal_inexact(first_num, second_num):
    try:
        result = Decimal(first_num).quantize(Decimal(second_num))
        assert True
    except BaseException:
        assert False

# Property 4: Rounding may occur if exponent of second operand is larger
@given(st.floats(allow_nan=False, allow_infinity=False), st.integers(min_value=0, max_value=5))
def test_rounding(first_num, second_exp):
    second_num = Decimal(10 ** second_exp)
    result = Decimal(first_num).quantize(second_num)
    assert result == Decimal(round(first_num, second_exp))

# Property 5: Errors should be signaled if exponent exceeds Emax or falls below Etiny
@given(st.floats(allow_nan=False, allow_infinity=False), st.integers(min_value=-10**5, max_value=10**5))
def test_exceeds_limits(first_num, second_exp):
    second_num = Decimal(10 ** second_exp)
    try:
        result = Decimal(first_num).quantize(second_num)
        assert second_num.as_tuple().exponent >= getcontext().Emin and second_num.as_tuple().exponent <= getcontext().Emax
    except InvalidOperation:
        assert not (second_num.as_tuple().exponent >= getcontext().Emin and second_num.as_tuple().exponent <= getcontext().Emax)