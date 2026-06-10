import decimal
from hypothesis import given, strategies as st, assume

@given(st.floats(allow_nan=False, allow_infinity=False))
def test_from_float_positive(num):
    if num >= 0:
        assert decimal.Decimal.from_float(num) >= 0

@given(st.floats(allow_nan=False, allow_infinity=False))
def test_from_float_negative(num):
    if num <= 0:
        assert decimal.Decimal.from_float(num) <= 0

@given(st.just(float('nan')))
def test_from_float_nan(num):
    assert decimal.Decimal.from_float(num).is_nan()

@given(st.just(float('inf')))
def test_from_float_positive_infinity(num):
    assert decimal.Decimal.from_float(num).is_infinite() and decimal.Decimal.from_float(num) > 0

@given(st.just(float('-inf')))
def test_from_float_negative_infinity(num):
    assert decimal.Decimal.from_float(num).is_infinite() and decimal.Decimal.from_float(num) < 0

@given(st.one_of(st.text(), st.lists(st.integers()), st.dictionaries(st.integers(), st.integers())))
def test_from_float_type_error(input_data):
    try:
        decimal.Decimal.from_float(input_data)
    except TypeError:
        pass