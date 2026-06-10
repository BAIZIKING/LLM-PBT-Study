from hypothesis import given, strategies as st
import zlib

# Summary: Generate a wide variety of byte string inputs, including
# empty strings, small strings, large strings, strings with null bytes, 
# and strings with non-ASCII characters. Test properties like:
# - The checksum is an unsigned 32-bit integer
# - Using value=1 (default) produces the same result as not specifying it
# - Concatenating inputs produces the same checksum as the full string
# - Checksum values are deterministic for the same input
@given(st.data())
def test_adler32(data):
    # Generate byte string of varying size
    buf = data.draw(st.binary(max_size=1024))
    
    # Generate optional starting checksum value
    value = data.draw(st.one_of(
        st.just(1),
        st.integers(min_value=0, max_value=2**32-1)))
    
    checksum = zlib.adler32(buf, value)
    
    assert isinstance(checksum, int)
    assert 0 <= checksum <= 2**32-1
    
    assert zlib.adler32(buf, 1) == zlib.adler32(buf)
    
    if buf:
        split = data.draw(st.integers(min_value=0, max_value=len(buf)-1))
        assert zlib.adler32(buf) == zlib.adler32(buf[:split], zlib.adler32(buf[split:]))
    
    assert zlib.adler32(buf) == zlib.adler32(buf)
# End program