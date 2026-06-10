from hypothesis import given, strategies as st
from decimal import Decimal

# Summary: Generate operands by mixing hypothesis's st.decimals (covering finite
# values, NaN, and infinities) with a sampled set of explicit edge cases
# (NaN, sNaN, +/-Inf, +/-0, small/large magnitudes). Both operands a and b are
# drawn independently to cover all combinations.
@given(st.data())
def test_decimal_Decimal_compare(data):
    edge_cases = st.sampled_from([
        Decimal('NaN'), Decimal('-NaN'), Decimal('sNaN'),
        Decimal('Infinity'), Decimal('-Infinity'),
        Decimal('0'), Decimal('-0'),
        Decimal('1'), Decimal('-1'),
        Decimal('1.5'), Decimal('-1.5'),
        Decimal('1E+10'), Decimal('-1E-10'),
        Decimal('123456789.123456789'),
    ])
    general = st.decimals(allow_nan=True, allow_infinity=True)
    operand = st.one_of(general, edge_cases)

    a = data.draw(operand, label="a")
    b = data.draw(operand, label="b")

    result = a.compare(b)

    # Property 1: result is always a Decimal
    assert isinstance(result, Decimal)

    a_is_nan = a.is_nan()
    b_is_nan = b.is_nan()

    if a_is_nan or b_is_nan:
        # Property 2: NaN handling -> result is a NaN
        assert result.is_nan()
    else:
        # Property 3: ordering correctness for non-NaN operands
        if a < b:
            assert result == Decimal('-1')
        elif a == b:
            assert result == Decimal('0')
        else:  # a > b
            assert result == Decimal('1')

        # Property 4: symmetry for non-NaN operands
        assert result == -b.compare(a)
# End program