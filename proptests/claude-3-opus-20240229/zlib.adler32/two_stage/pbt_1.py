from hypothesis import given, strategies as st
import zlib

@given(st.binary())
def test_result_is_unsigned_32bit_integer(data):
    result = zlib.adler32(data)
    assert 0 <= result < 2**32

@given(st.binary(), st.integers(min_value=1, max_value=2**32-1))
def test_empty_input_returns_initial_value(data, initial_value):
    result = zlib.adler32(b'', initial_value)
    assert result == initial_value

@given(st.binary(), st.binary())
def test_concatenation_checksum(data1, data2):
    checksum1 = zlib.adler32(data1)
    checksum2 = zlib.adler32(data2, checksum1)
    combined_checksum = zlib.adler32(data1 + data2)
    assert checksum2 == combined_checksum

@given(st.binary())
def test_not_cryptographically_strong(data):
    # This test is just a placeholder to remind that adler32 is not cryptographically strong
    # and should not be used for authentication or digital signatures.
    pass

@given(st.binary(), st.integers(min_value=1, max_value=2**32-1))
def test_deterministic_checksum(data, initial_value):
    checksum1 = zlib.adler32(data, initial_value)
    checksum2 = zlib.adler32(data, initial_value)
    assert checksum1 == checksum2
# End program