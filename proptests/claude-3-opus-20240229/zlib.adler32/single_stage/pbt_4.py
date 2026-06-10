from hypothesis import given, strategies as st
import zlib

# Summary: 
# Generate a wide variety of byte strings to test, including:
# - Empty byte string 
# - Random short byte strings
# - Random "large" byte strings up to 1MB in size
# - A random starting checksum value or use the default of 1
#
# Check the following properties:
# - Result is an unsigned 32-bit integer
# - Checksum of empty string is 1 (with default starting value) 
# - Checksum is deterministic - same input always produces same output
# - Concatenating inputs is equivalent to computing running checksum
@given(data=st.data())
def test_adler32(data):
    # Generate random byte string
    input_bytes = data.draw(st.one_of(
        st.binary(max_size=0),  # empty
        st.binary(max_size=100),  # short 
        st.binary(max_size=1000000)))  # large
    
    # Randomly use default checksum or generate a random one
    use_default_start = data.draw(st.booleans())
    if use_default_start:
        checksum = zlib.adler32(input_bytes)
    else:
        start_value = data.draw(st.integers(min_value=0, max_value=2**32-1)) 
        checksum = zlib.adler32(input_bytes, start_value)
        
    # Check result is unsigned 32-bit int
    assert 0 <= checksum <= 2**32 - 1
    
    # Check empty input returns 1 with default start
    if len(input_bytes) == 0 and use_default_start:
        assert checksum == 1
        
    # Check deterministic
    if use_default_start:
        assert zlib.adler32(input_bytes) == checksum
    else:
        assert zlib.adler32(input_bytes, start_value) == checksum
        
    # Check concatenation equivalent to running checksum  
    if len(input_bytes) >= 2:
        part1 = input_bytes[:len(input_bytes)//2] 
        part2 = input_bytes[len(input_bytes)//2:]
        if use_default_start:
            check1 = zlib.adler32(part1)
            full = zlib.adler32(input_bytes)
        else:
            check1 = zlib.adler32(part1, start_value)
            full = zlib.adler32(input_bytes, start_value)
        check2 = zlib.adler32(part2, check1)
        assert check2 == full
# End program        