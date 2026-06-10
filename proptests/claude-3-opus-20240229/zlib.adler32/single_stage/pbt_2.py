from hypothesis import given, strategies as st
import zlib

# Generate a variety of random byte strings to test, including:
# - Empty byte string 
# - Short byte strings
# - Very long byte strings (up to 1 MB in size)
# - Byte strings with null bytes
# Also generate random unsigned 32-bit integers to use as the initial checksum value
@given(data=st.data())
def test_adler32(data):
    # Generate random input data
    input_bytes = data.draw(st.one_of(
        st.just(b''),  # empty
        st.binary(max_size=10),  # short 
        st.binary(max_size=1000000), # very long
        st.binary(max_size=100).filter(lambda b: b'\x00' in b) # contains null
    ))
    init_value = data.draw(st.integers(min_value=0, max_value=2**32-1))
    
    # Properties to check:
    # 1. Result is an unsigned 32-bit integer 
    # 2. Same input always produces same output
    # 3. Changing initial value changes checksum result
    # 4. Checksum is different for different inputs (with high probability)
    result1 = zlib.adler32(input_bytes, init_value) 
    assert 0 <= result1 <= 2**32 - 1
    assert zlib.adler32(input_bytes, init_value) == result1
    
    if init_value > 0:
        assert zlib.adler32(input_bytes, init_value-1) != result1
    else:
        assert zlib.adler32(input_bytes, init_value+1) != result1
        
    if len(input_bytes) > 0: 
        assert zlib.adler32(input_bytes + b'x') != result1
# End program