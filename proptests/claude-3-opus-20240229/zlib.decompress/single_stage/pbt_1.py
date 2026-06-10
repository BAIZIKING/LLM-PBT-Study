from hypothesis import given, strategies as st
import zlib

# Summary: Generate a wide variety of compressed byte strings to test zlib.decompress
# - Generate random byte strings of varying lengths
# - Compress them using different window sizes (wbits) covering key ranges: 
#   - +8 to +15 for zlib w/ header
#   - -8 to -15 for raw deflate  
#   - +24 to +31 for gzip
#   - +40 to +47 for auto-detect
# - Decompress with matching wbits and check roundtrip equality
# - Try decompressing with mismatched wbits and expect errors
# - Try decompressing corrupted data and expect errors
@given(data=st.data())
def test_zlib_decompress(data):
    input_bytes = data.draw(st.binary(min_size=0, max_size=1024))
    wbits = data.draw(st.sampled_from(range(8,16) + range(-15,-7) + range(24,32) + range(40,48)))
    
    compressed = zlib.compress(input_bytes, wbits)
    
    # Check decompress with correct wbits produces original input  
    assert zlib.decompress(compressed, wbits) == input_bytes
    
    # Check decompress with mismatched wbits raises error
    if wbits >= 0:
        with pytest.raises(zlib.error):
            zlib.decompress(compressed, wbits=-wbits) 
    else:
        with pytest.raises(zlib.error):  
            zlib.decompress(compressed, wbits=-wbits)

    # Check decompress of corrupted data raises error
    corrupted = bytearray(compressed)
    corrupted[len(corrupted)//2] ^= 0xff
    with pytest.raises(zlib.error):
        zlib.decompress(corrupted, wbits)
# End program        