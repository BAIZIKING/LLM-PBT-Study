from hypothesis import given, strategies as st
from decimal import Decimal

# Summary: Generate two Decimals mixing st.decimals() (with NaN/Infinity allowed)
# and explicitly sampled special values (NaN, +/-Inf, +/-0). Signaling NaNs are
# excluded since they raise InvalidOperation rather than returning a result.
# Verify: return type is Decimal; NaN operand => NaN; otherwise result is in
# {-1, 0, 1} consistent with Python's <, ==, > comparison of the operands.
@given(st.data())
def test_decimal_Decimal_compare(data):
    special = st.sampled_from([
        Decimal('NaN'), Decimal('-NaN'),
        Decimal('Infinity'), Decimal('-Infinity'),
        Decimal('0'), Decimal('-0'),
        Decimal('1'), Decimal('-1'),
    ])
    finite = st.decimals(allow_nan=True, allow_infinity=True)
    dec_strategy = st.one_of(special, finite)

    a = data.draw(dec_strategy)
    b = data.draw(dec_strategy)

    result = a.compare(b)

    # Property 1: result is always a Decimal
    assert isinstance(result, Decimal)

    if a.is_nan() or b.is_nan():
        # Property 2: NaN operand => NaN result
        assert result.is_nan()
    else:
        # Property 6: non-NaN result must be -1, 0, or 1
        assert result in (Decimal('-1'), Decimal('0'), Decimal('1'))
        # Properties 3, 4, 5: consistent with ordering
        if a < b:
            assert result == Decimal('-1')
        elif a == b:
            assert result == Decimal('0')
        else:  # a > b
            assert result == Decimal('1')
# End program