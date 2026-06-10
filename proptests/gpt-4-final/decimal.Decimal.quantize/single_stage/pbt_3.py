from hypothesis import given, strategies as st
from decimal import Decimal, getcontext

@given(st.floats(allow_nan=False, allow_infinity=False), st.integers(-3, 3))
def test_decimal_quantize(float_num, exp):
    context = getcontext()
    dec_num = Decimal(float_num).quantize(Decimal(10) ** exp)
    assert dec_num.as_tuple().exponent == exp

    with getcontext() as ctx:
        ctx.prec = 2
        if abs(float_num) >= 10 ** (exp+2):  # would lead to a coefficient larger than precision
            try:
                Decimal(float_num).quantize(Decimal(10) ** exp)
            except InvalidOperation:
                assert True
            else:
                assert False
        else:
            Decimal(float_num).quantize(Decimal(10) ** exp, context=ctx)  # precision-needing operation
# End program