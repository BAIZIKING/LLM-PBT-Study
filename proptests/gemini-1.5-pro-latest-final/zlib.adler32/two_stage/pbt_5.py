from hypothesis import given, strategies as st
import zlib

# Property 1: Output is an unsigned 32-bit integer
@given(st.binary()) 
def test_adler32_unsigned_int(data):
    checksum = zlib.adler32(data)
    assert 0 <= checksum <= 2**32 - 1

# Property 2: Identical inputs yield the same output
@given(st.binary())
def test_adler32_deterministic(data):
    checksum1 = zlib.adler32(data)
    checksum2 = zlib.adler32(data)
    assert checksum1 == checksum2

# Property 3: Order of concatenation does not matter
@given(st.binary(), st.binary())
def test_adler32_concatenation_order(data1, data2):
    checksum1 = zlib.adler32(data1 + data2)
    checksum2 = zlib.adler32(data2 + data1)
    assert checksum1 == checksum2 

# Property 4: Empty input yields initial value
@given(st.integers(min_value=1, max_value=2**32-1))
def test_adler32_empty_input(value):
    checksum = zlib.adler32(b"", value)
    assert checksum == value

# Property 5: Single byte modification changes output
@given(st.binary(min_size=1), st.integers(min_value=0, max_value=255))
def test_adler32_single_byte_change(data, byte):
    modified_data = bytearray(data)
    modified_data[0] = byte
    checksum1 = zlib.adler32(data)
    checksum2 = zlib.adler32(modified_data)
    assert checksum1 != checksum2
# End program 