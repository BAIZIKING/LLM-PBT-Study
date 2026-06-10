from hypothesis import given, strategies as st
import zlib

@given(data=st.binary(max_size=4096))
def test_zlib_adler32_output_is_integer(data):
    result = zlib.adler32(data)
    assert isinstance(result, int)
# End program

@given(data=st.binary(max_size=4096), value=st.integers(min_value=0, max_value=2**32 - 1))
def test_zlib_adler32_output_is_unsigned_32bit(data, value):
    result = zlib.adler32(data, value)
    assert 0 <= result <= 2**32 - 1
# End program

@given(st.data())
def test_zlib_adler32_empty_default_value(data):
    result = zlib.adler32(b"")
    assert result == 1
# End program

@given(data=st.binary(max_size=4096), value=st.integers(min_value=0, max_value=2**32 - 1))
def test_zlib_adler32_deterministic(data, value):
    result1 = zlib.adler32(data, value)
    result2 = zlib.adler32(data, value)
    assert result1 == result2
# End program

@given(data1=st.binary(max_size=4096), data2=st.binary(max_size=4096))
def test_zlib_adler32_running_checksum(data1, data2):
    combined = zlib.adler32(data1 + data2)
    running = zlib.adler32(data2, zlib.adler32(data1))
    assert combined == running
# End program