from hypothesis import given, strategies as st
import decimal
from decimal import Decimal

# Strategy for generating Decimal instances, including NaNs, infinities,
# and a wide range of finite values, while being careful about overflows.
decimal_strategy = st.one_of(
    st.decimals(allow_nan=True, allow_infinity=True),
    st.integers(min_value=-10**50, max_value=10**50).map(Decimal),
    st.sampled_from([
        Decimal('NaN'), Decimal('-NaN'), Decimal('sNaN'),
        Decimal('Infinity'), Decimal('-Infinity'),
        Decimal('0'), Decimal('-0'), Decimal('1'), Decimal('-1'),
    ]),
)


def is_nan(d):
    return d.is_nan()


@given(st.data())
def test_compare_result_is_one_of_four_values(data):
    a = data.draw(decimal_strategy)
    b = data.draw(decimal_strategy)
    try:
        result = a.compare(b)
    except decimal.InvalidOperation:
        # sNaN can trigger InvalidOperation under default context
        return
    assert isinstance(result, Decimal)
    assert (result.is_nan() or
            result == Decimal('-1') or
            result == Decimal('0') or
            result == Decimal('1'))
# End program


@given(st.data())
def test_compare_nan_propagation(data):
    a = data.draw(decimal_strategy)
    b = data.draw(decimal_strategy)
    try:
        result = a.compare(b)
    except decimal.InvalidOperation:
        return
    if is_nan(a) or is_nan(b):
        assert result.is_nan()
    else:
        assert not result.is_nan()
        assert result in (Decimal('-1'), Decimal('0'), Decimal('1'))
# End program


@given(st.data())
def test_compare_consistent_with_operators(data):
    a = data.draw(decimal_strategy)
    b = data.draw(decimal_strategy)
    try:
        result = a.compare(b)
    except decimal.InvalidOperation:
        return
    if is_nan(a) or is_nan(b):
        return
    if a < b:
        assert result == Decimal('-1')
    elif a == b:
        assert result == Decimal('0')
    else:
        assert result == Decimal('1')
# End program


@given(st.data())
def test_compare_antisymmetry(data):
    a = data.draw(decimal_strategy)
    b = data.draw(decimal_strategy)
    try:
        forward = a.compare(b)
        backward = b.compare(a)
    except decimal.InvalidOperation:
        return
    if is_nan(a) or is_nan(b):
        return
    assert forward == -backward
# End program


@given(st.data())
def test_compare_reflexivity(data):
    a = data.draw(decimal_strategy)
    try:
        result = a.compare(a)
    except decimal.InvalidOperation:
        return
    if is_nan(a):
        assert result.is_nan()
    else:
        assert result == Decimal('0')
# End program