from hypothesis import given, strategies as st
import decimal

def _finite_decimal_strategy():
    return st.builds(
        lambda sign, coeff, exp: decimal.Decimal(
            (sign, tuple(int(d) for d in str(coeff)), exp)
        ),
        st.integers(min_value=0, max_value=1),
        st.integers(min_value=0, max_value=10**18),
        st.integers(min_value=-18, max_value=18),
    )

_NON_NAN_DECIMALS = st.one_of(
    _finite_decimal_strategy(),
    st.sampled_from([
        decimal.Decimal("Infinity"),
        decimal.Decimal("-Infinity"),
    ]),
)

_NAN_DECIMALS = st.sampled_from([
    decimal.Decimal("NaN"),
    decimal.Decimal("-NaN"),
])

def _ordered_decimal_pair(data):
    base = data.draw(st.integers(min_value=-(10**9), max_value=10**9))
    delta = data.draw(st.integers(min_value=1, max_value=10**9))
    exp = data.draw(st.integers(min_value=-9, max_value=9))
    smaller = decimal.Decimal(f"{base}e{exp}")
    larger = decimal.Decimal(f"{base + delta}e{exp}")
    return smaller, larger

@given(st.data())
def test_decimal_Decimal_compare_nan_operand_property(data):
    nan_value = data.draw(_NAN_DECIMALS)
    other = data.draw(st.one_of(_NON_NAN_DECIMALS, _NAN_DECIMALS))

    if data.draw(st.booleans()):
        result = nan_value.compare(other)
    else:
        result = other.compare(nan_value)

    assert isinstance(result, decimal.Decimal)
    assert result.is_nan()

@given(st.data())
def test_decimal_Decimal_compare_non_nan_result_set_property(data):
    left = data.draw(_NON_NAN_DECIMALS)
    right = data.draw(_NON_NAN_DECIMALS)

    result = left.compare(right)

    assert isinstance(result, decimal.Decimal)
    assert result in (
        decimal.Decimal("-1"),
        decimal.Decimal("0"),
        decimal.Decimal("1"),
    )

@given(st.data())
def test_decimal_Decimal_compare_less_than_property(data):
    left, right = _ordered_decimal_pair(data)

    result = left.compare(right)

    assert result == decimal.Decimal("-1")

@given(st.data())
def test_decimal_Decimal_compare_equal_property(data):
    value = data.draw(_NON_NAN_DECIMALS)

    result = value.compare(value)

    assert result == decimal.Decimal("0")

@given(st.data())
def test_decimal_Decimal_compare_greater_than_property(data):
    smaller, larger = _ordered_decimal_pair(data)

    result = larger.compare(smaller)

    assert result == decimal.Decimal("1")

# End program