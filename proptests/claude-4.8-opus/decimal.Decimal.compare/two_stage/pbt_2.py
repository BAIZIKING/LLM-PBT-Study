from hypothesis import given, strategies as st
import decimal
from decimal import Decimal


@given(st.data())
def test_decimal_Decimal_compare_property(data):
    # Strategy for Decimal values: bounded finite numbers plus special values.
    finite = st.builds(
        Decimal,
        st.decimals(
            allow_nan=False,
            allow_infinity=False,
            min_value=Decimal("-1e50"),
            max_value=Decimal("1e50"),
        ),
    )
    special = st.sampled_from(
        [
            Decimal("NaN"),
            Decimal("-NaN"),
            Decimal("Infinity"),
            Decimal("-Infinity"),
            Decimal("0"),
            Decimal("-0"),
        ]
    )
    decimal_strategy = st.one_of(finite, special)

    a = data.draw(decimal_strategy)
    b = data.draw(decimal_strategy)

    result = a.compare(b)

    a_is_nan = a.is_nan()
    b_is_nan = b.is_nan()
    either_nan = a_is_nan or b_is_nan

    # Property 1: The result is always a Decimal instance.
    assert isinstance(result, Decimal)

    # Property 3: If either operand is a NaN, the result is NaN.
    if either_nan:
        assert result.is_nan()
    else:
        # Property 2: For non-NaN operands the result is exactly -1, 0, or 1.
        assert result in (Decimal("-1"), Decimal("0"), Decimal("1"))

        # Property 5: Result is consistent with standard comparison operators.
        if a < b:
            assert result == Decimal("-1")
        elif a == b:
            assert result == Decimal("0")
        else:
            assert result == Decimal("1")

        # Property 4: Antisymmetry: compare(a, b) == -compare(b, a).
        reverse = b.compare(a)
        assert result == -reverse
# End program