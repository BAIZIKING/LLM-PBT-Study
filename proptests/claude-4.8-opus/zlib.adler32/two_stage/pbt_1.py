from hypothesis import given, strategies as st
import zlib

# Property 1: The output is always an integer.
@given(data=st.binary(max_size=4096), value=st.one_of(st.none(), st.integers(min_value=0, max_value=2**32 - 1)))
def test_zlib_adler32_output_is_integer(data, value):
    if value is None:
        result = zlib.adler32(data)
    else:
        result = zlib.adler32(data, value)
    assert isinstance(result, int)
# End program


# Property 2: The output is always an unsigned 32-bit integer (0 <= result <= 2**32 - 1).
@given(data=st.binary(max_size=4096), value=st.one_of(st.none(), st.integers(min_value=0, max_value=2**32 - 1)))
def test_zlib_adler32_output_is_unsigned_32bit(data, value):
    if value is None:
        result = zlib.adler32(data)
    else:
        result = zlib.adler32(data, value)
    assert 0 <= result <= 2**32 - 1
# End program


# Property 3: Running checksum over concatenation equals chaining via value argument.
@given(data1=st.binary(max_size=4096), data2=st.binary(max_size=4096))
def test_zlib_adler32_running_checksum(data1, data2):
    full = zlib.adler32(data1 + data2)
    chained = zlib.adler32(data2, zlib.adler32(data1))
    assert full == chained
# End program


# Property 4: Determinism - same inputs always produce same output.
@given(data=st.binary(max_size=4096), value=st.one_of(st.none(), st.integers(min_value=0, max_value=2**32 - 1)))
def test_zlib_adler32_determinism(data, value):
    if value is None:
        result1 = zlib.adler32(data)
        result2 = zlib.adler32(data)
    else:
        result1 = zlib.adler32(data, value)
        result2 = zlib.adler32(data, value)
    assert result1 == result2
# End program


# Property 5: Empty data returns default 1 (no value) or the given value (after unsigned normalization).
@given(value=st.one_of(st.none(), st.integers(min_value=0, max_value=2**32 - 1)))
def test_zlib_adler32_empty_data(value):
    if value is None:
        assert zlib.adler32(b"") == 1
    else:
        assert zlib.adler32(b"", value) == (value & (2**32 - 1))
# End program