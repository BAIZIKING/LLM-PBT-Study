from hypothesis import given, strategies as st
from decimal import Decimal, InvalidOperation

# Summary: Generate two Decimals using st.decimals() (allowing NaN/Infinity)
# combined with explicitly sampled special-value strings (NaN, sNaN, Infinity,
# -Infinity, -0). Then verify compare() returns a Decimal, yields NaN when an
# operand is NaN, and otherwise returns -1/0/1 consistent with the ordering.
@given(st.data())
def test_decimal_Decimal_compare(data):
    def make_decimal():
        special = st.sampled_from(
            ["NaN", "-NaN", "sNaN", "Infinity", "-Infinity",
             "0", "-0", "1.0", "1.00", "-1", "1e10", "1e-10"]
        ).map(Decimal)
        normal = st.decimals(allow_nan=True, allow_infinity=True)
        return st.one_of(normal, special)

    a = data.draw(make_decimal())
    b = data.draw(make_decimal())

    # Signaling NaNs raise InvalidOperation under default context; that is
    # valid behavior, so we skip those cases for the value-based properties.
    try:
        result = a.compare(b)
    except InvalidOperation:
        assert a.is_snan() or b.is_snan()
        return

    # Property 1: result is always a Decimal instance.
    assert isinstance(result, Decimal)

    # Property 2: if either operand is a (quiet) NaN, result is NaN.
    if a.is_nan() or b.is_nan():
        assert result.is_nan()
        return

    # Property 3 & 4: result must be -1, 0, or 1, consistent with ordering.
    assert result in (Decimal("-1"), Decimal("0"), Decimal("1"))
    if a < b:
        assert result == Decimal("-1")
    elif a == b:
        assert result == Decimal("0")
    else:  # a > b
        assert result == Decimal("1")
# End program