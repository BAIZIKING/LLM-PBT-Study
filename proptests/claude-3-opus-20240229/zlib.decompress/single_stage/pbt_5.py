from hypothesis import given, strategies as st
import zlib

# Summary: Generate a wide variety of compressed byte strings to test zlib.decompress
# - Generate random byte strings of varying lengths
# - Compress them using different window sizes (wbits) covering the allowed ranges 
# - Generate both valid zlib and gzip headers
# - Mix in some invalid compressed data as well
# For each input, check:
# - Result is a byte string that decompresses to the original data
# - Decompressing with too small a window size raises an error
# - Decompressing invalid data raises an error
@given(st.data())
def test_zlib_decompress(data):
    original = data.draw(st.binary())
    wbits = data.draw(st.sampled_from([8, 9, 10, 11, 12, 13, 14, 15, 0, -8, -9, -10, -11, -12, -13, -14, -15, 
                                       24, 25, 26, 27, 28, 29, 30, 31, 40, 41, 42, 43, 44, 45, 46, 47]))
    if wbits >= 24:
        header = b'\x1f\x8b' # gzip header
    elif wbits >= 0:  
        header = b'\x78\x9c' # zlib header
    else:
        header = b''
        
    if data.draw(st.booleans()):
        # Valid compressed data
        compressed = header + zlib.compress(original, level=6)[2:-4]
    else:
        # Invalid data
        compressed = header + data.draw(st.binary())
        
    if wbits < 0:
        wbits = -wbits
        
    # Check decompress result matches original    
    assert zlib.decompress(compressed, wbits=wbits) == original
    
    # Check error raised if window too small
    if len(original) > 0:
        with pytest.raises(zlib.error):
            zlib.decompress(compressed, wbits=8)
            
    # Check error raised on invalid data  
    if not data.draw(st.booleans()):  
        with pytest.raises(zlib.error):
            zlib.decompress(compressed, wbits=wbits)
# End program            