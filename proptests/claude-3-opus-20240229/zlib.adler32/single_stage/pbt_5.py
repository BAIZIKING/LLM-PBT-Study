from hypothesis import given, strategies as st
import zlib

# Generate a wide variety of byte string inputs, including:
# - Empty byte string 
# - Single byte strings
# - Byte strings with various lengths
# - Byte strings with null bytes
# Also generate optional starting checksum values that are:
# - Unsigned 32-bit integers
# - Includes boundary values 0 and 2**32-1
@given(data=st.data())
def test_adler32(data):
    value = data.draw(st.integers(min_value=0, max_value=2**32-1), label='value')
    input_bytes = data.draw(st.binary(), label='input_bytes')
    
    # Property 1: Result is unsigned 32-bit int
    assert 0 <= zlib.adler32(input_bytes, value) <= 2**32-1
    
    # Property 2: Default value is 1
    assert zlib.adler32(input_bytes) == zlib.adler32(input_bytes, 1)
    
    # Property 3: Concatenation of inputs
    part1 = data.draw(st.binary(), label='part1') 
    part2 = data.draw(st.binary(), label='part2')
    assert zlib.adler32(part1 + part2, value) == zlib.adler32(part2, zlib.adler32(part1, value))
# End program