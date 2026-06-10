from hypothesis import given, strategies as st
import zlib

UINT32_MAX = 2**32 - 1


@given(st.data())
def test_zlib_adler32_result_is_unsigned_32_bit_integer(data):
    payload = data.draw(st.binary(max_size=8192))
    value = data.draw(st.integers(min_value=0, max_value=UINT32_MAX))

    result = zlib.adler32(payload, value)

    assert isinstance(result, int)
    assert 0 <= result <= UINT32_MAX


@given(st.data())
def test_zlib_adler32_is_deterministic(data):
    payload = data.draw(st.binary(max_size=8192))
    value = data.draw(st.integers(min_value=0, max_value=UINT32_MAX))

    result1 = zlib.adler32(payload, value)
    result2 = zlib.adler32(payload, value)

    assert result1 == result2


@given(st.data())
def test_zlib_adler32_default_value_is_one(data):
    payload = data.draw(st.binary(max_size=8192))

    result_with_default = zlib.adler32(payload)
    result_with_explicit_one = zlib.adler32(payload, 1)

    assert result_with_default == result_with_explicit_one


@given(st.data())
def test_zlib_adler32_can_be_computed_incrementally(data):
    first = data.draw(st.binary(max_size=4096))
    second = data.draw(st.binary(max_size=4096))
    value = data.draw(st.integers(min_value=0, max_value=UINT32_MAX))

    direct_result = zlib.adler32(first + second, value)
    incremental_result = zlib.adler32(second, zlib.adler32(first, value))

    assert direct_result == incremental_result


@given(st.data())
def test_zlib_adler32_empty_input_returns_starting_value(data):
    value = data.draw(st.integers(min_value=0, max_value=UINT32_MAX))

    result = zlib.adler32(b"", value)

    assert result == value


# End program