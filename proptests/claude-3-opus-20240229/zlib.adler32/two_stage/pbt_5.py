from hypothesis import given, strategies as st
import zlib

@given(st.binary())
def test_result_is_unsigned_32bit_int(data):
    result = zlib.adler32(data)
    assert 0 <= result <= 2**32 - 1

@given(st.integers(min_value=0, max_value=2**32 - 1))
def test_empty_input_returns_initial_value(value):
    assert zlib.adler32(b'', value) == value

@given(st.binary(), st.integers(min_value=0, max_value=2**32 - 1))
def test_checksum_is_deterministic(data, value):
    result1 = zlib.adler32(data, value)
    result2 = zlib.adler32(data, value)
    assert result1 == result2

@given(st.binary(max_size=1000))
def test_checksum_is_not_cryptographically_strong(data):
    # This test is just a placeholder to document the property
    pass

@given(st.binary(max_size=1000), st.binary(max_size=1000))
def test_checksum_of_concatenation(data1, data2):
    combined_checksum = zlib.adler32(data1 + data2)
    checksum1 = zlib.adler32(data1)
    checksum2 = zlib.adler32(data2, checksum1)
    assert combined_checksum == checksum2
# End program