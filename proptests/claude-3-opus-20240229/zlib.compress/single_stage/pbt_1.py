from hypothesis import given, strategies as st
import zlib

# Summary: Generate a wide variety of byte string inputs, including empty strings, 
# small strings, large strings, and strings with special characters.
# Test different compression levels from 0 to 9 and -1 (default).
# Test different window size logarithms using the wbits parameter.
# Properties to check:
# 1. The output should be a bytes object
# 2. The output size should be less than or equal to the input size when level > 0
# 3. The output should be identical to input when level = 0 (no compression)
# 4. Decompressing the compressed output should yield the original input data
@given(data=st.data())
def test_zlib_compress(data):
    input_bytes = data.draw(st.binary())
    level = data.draw(st.integers(min_value=-1, max_value=9))
    wbits_choices = st.integers(min_value=-15, max_value=-9) | st.integers(min_value=9, max_value=15) | st.integers(min_value=25, max_value=31)
    wbits = data.draw(wbits_choices)
    
    compressed = zlib.compress(input_bytes, level=level, wbits=wbits)
    
    assert isinstance(compressed, bytes)
    if level > 0:
        assert len(compressed) <= len(input_bytes)
    if level == 0:
        assert compressed == input_bytes
    decompressed = zlib.decompress(compressed, wbits=wbits)
    assert decompressed == input_bytes
# End program