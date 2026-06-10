from hypothesis import given, strategies as st
from decimal import Decimal, InvalidOperation

# Summary: Generate two Decimals via a custom strategy mixing finite numbers
# (st.decimals) and special values (NaN, sNaN, +/-Infinity, +/-0). Occasionally
# force b == a to reliably exercise the equality case. Check return type and the
# four documented outcomes: NaN-propagation, -1 (a<b), 0 (a==b), 1 (a>b).
@given(st.data())
def test_decimal_Decimal_compare(data):
    # Strategy producing a variety of Decimals including edge cases.
    special = st.sampled_from([
        Decimal('NaN'), Decimal('-NaN'),
        Decimal('sNaN'),
        Decimal('Infinity'), Decimal('-Infinity'),
        Decimal('0'), Decimal('-0'),
        Decimal('1'), Decimal('-1'),
    ])
    finite = st.decimals(allow_nan=False, allow_infinity=False)
    decimal_strategy = st.one_of(finite, special)

    a = data.draw(decimal_strategy, label="a")
    # Occasionally reuse a to hit the equality branch deterministically.
    if data.draw(st.booleans(), label="reuse"):
        b = a
    else:
        b = data.draw(decimal_strategy, label="b")

    a_is_snan = a.is_snan()
    b_is_snan = b.is_snan()

    # Signaling NaN triggers InvalidOperation in comparison context.
    if a_is_snan or b_is_snan:
        try:
            a.compare(b)
        except InvalidOperation:
            return  # Expected behavior for sNaN; nothing more to check.
        # If no exception, fall through to validate the result below.

    result = a.compare(b)

    # Property 1: result is always a Decimal.
    assert isinstance(result, Decimal)

    a_is_nan = a.is_nan()
    b_is_nan = b.is_nan()

    if a_is_nan or b_is_nan:
        # Property 2: NaN operand => NaN result.
        assert result.is_nan()
    elif a < b:
        # Property 3: a < b => -1.
        assert result == Decimal('-1')
    elif a == b:
        # Property 4: a == b => 0.
        assert result == Decimal('0')
    else:
        # Property 5: a > b => 1.
        assert a > b
        assert result == Decimal('1')
# End program