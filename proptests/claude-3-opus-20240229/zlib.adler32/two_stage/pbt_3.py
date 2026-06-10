from hypothesis import given, strategies as st
import zlib

@given(st.binary())
def test_result_is_unsigned_32bit_int(data):
    result = zlib.adler32(data)
    assert 0 <= result <= 2**32 - 1

@given(st.integers(min_value=0, max_value=2**32 - 1))
def test_empty_input_with_starting_value(value):
    result = zlib.adler32(b'', value)
    assert result == value

@given(st.binary(), st.binary(), st.integers(min_value=0, max_value=2**32 - 1))
def test_concatenation_property(data1, data2, value):
    result1 = zlib.adler32(data1, value)
    result2 = zlib.adler32(data2, result1)
    combined_result = zlib.adler32(data1 + data2, value)
    assert result2 == combined_result

@given(st.binary(), st.integers(min_value=0, max_value=2**32 - 1))
def test_deterministic_output(data, value):
    result1 = zlib.adler32(data, value)
    result2 = zlib.adler32(data, value)
    assert result1 == result2
# End program