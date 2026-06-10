from hypothesis import given, strategies as st
from decimal import Decimal
from math import gcd

# Summary: Generate finite Decimals from raw (sign, digits, exponent) triples to cover signed
# zeros, varied digit lengths/patterns, and very large/small powers of ten; also generate
# infinities, quiet NaNs, signaling NaNs, signed specials, and NaNs with payloads. For finite
# values, check that as_integer_ratio() returns two ints, the denominator is positive, the
# ratio is in lowest terms, and it equals an independently reduced exact ratio computed from
# the Decimal tuple. For infinities and NaNs, check the documented exceptions.
@given(st.data())
def test_decimal_Decimal_as_integer_ratio(data):
    digit_patterns = st.one_of(
        st.just((0,)),
        st.just((1,)),
        st.just((9,)),
        st.just((1, 0)),
        st.just((1, 0, 0, 0, 0, 0)),
        st.just(tuple([9] * 50)),
        st.just(tuple([1] + [0] * 50)),
        st.lists(st.integers(min_value=0, max_value=9), min_size=1, max_size=80).map(tuple),
    )

    exponent_values = st.one_of(
        st.integers(min_value=-100, max_value=100),
        st.sampled_from([-1000, -100, -28, -1, 0, 1, 28, 100, 1000]),
    )

    finite_decimals = st.tuples(
        st.integers(min_value=0, max_value=1),
        digit_patterns,
        exponent_values,
    ).map(Decimal)

    special_decimals = st.sampled_from(
        [
            "Infinity",
            "-Infinity",
            "NaN",
            "-NaN",
            "sNaN",
            "-sNaN",
            "NaN123",
            "-sNaN456",
        ]
    ).map(Decimal)

    x = data.draw(st.one_of(finite_decimals, special_decimals))

    if x.is_infinite():
        try:
            x.as_integer_ratio()
        except OverflowError:
            return
        assert False, "infinities must raise OverflowError"

    if x.is_nan():
        try:
            x.as_integer_ratio()
        except ValueError:
            return
        assert False, "NaNs must raise ValueError"

    n, d = x.as_integer_ratio()

    assert isinstance(n, int)
    assert isinstance(d, int)
    assert d > 0
    assert gcd(abs(n), d) == 1

    sign, digits, exponent = x.as_tuple()
    coefficient = 0
    for digit in digits:
        coefficient = coefficient * 10 + digit
    if sign:
        coefficient = -coefficient

    if exponent >= 0:
        expected_n = coefficient * (10 ** exponent)
        expected_d = 1
    else:
        expected_n = coefficient
        expected_d = 10 ** (-exponent)

    factor = gcd(abs(expected_n), expected_d)
    expected_n //= factor
    expected_d //= factor

    assert (n, d) == (expected_n, expected_d)
# End program