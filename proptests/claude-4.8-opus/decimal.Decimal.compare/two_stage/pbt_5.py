from hypothesis import given, strategies as st
import decimal
from decimal import Decimal


def decimal_strategy():
    finite = st.decimals(
        allow_nan=False,
        allow_infinity=False,
        min_value=Decimal("-1e25"),
        max_value=Decimal("1e25"),
        places=None,
    )
    specials = st.sampled_from([
        Decimal("NaN"),
        Decimal("-NaN"),
        Decimal("Infinity"),
        Decimal("-Infinity"),
        Decimal("0"),
        Decimal("-0"),
    ])
    return st.one_of(finite, specials)


@given(st.data())
def test_decimal_Decimal_compare_property(data):
    a = data.draw(decimal_strategy())
    b = data.draw(decimal_strategy())

    result = a.compare(b)

    # Property 1: The result is always a Decimal instance.
    assert isinstance(result, Decimal)

    a_is_nan = a.is_nan()
    b_is_nan = b.is_nan()

    if a_is_nan or b_is_nan:
        # Property 3: If either operand is a NaN, the result is a NaN.
        assert result.is_nan()
    else:
        # Property 2: For non-NaN operands, result is exactly -1, 0, or 1.
        assert result in (Decimal("-1"), Decimal("0"), Decimal("1"))

        # Property 5: Correctness of the comparison relative to numeric ordering.
        if a == b:
            assert result == Decimal("0")
        elif a < b:
            assert result == Decimal("-1")
        else:  # a > b
            assert result == Decimal("1")

        # Property 4: Antisymmetry. compare(a, b) == -compare(b, a).
        reverse = b.compare(a)
        assert result == -reverse
# End program