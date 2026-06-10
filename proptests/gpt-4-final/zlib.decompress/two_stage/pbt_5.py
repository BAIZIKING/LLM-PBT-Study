from hypothesis import given, strategies as st
import zlib

# Initialize a compressor object with a random wbits value
compressor = zlib.compressobj(wbits=15)

@given(st.binary(min_size=1, max_size=1000))
def test_zlib_decompress_property(binary_data):
    # Property 1 - decompressed data must always return bytes
    compressed_data = compressor.compress(binary_data) + compressor.flush()
    assert isinstance(zlib.decompress(compressed_data, wbits=15), bytes)
    
    # Property 2 - the length of decompressed data should be greater or equal to the compressed data
    decompressed_data = zlib.decompress(compressed_data, wbits=15)
    assert len(decompressed_data) >= len(compressed_data)
    
    # Property 3 and 4 - it should raise an exception when wbits value is small or input data doesn't have right headers
    with pytest.raises(Exception):
        zlib.decompress(compressed_data, wbits=8)
        zlib.decompress(binary_data, wbits=15)

    # Property 5 - decompression should work fine even if data larger than default buffer size
    bufsize = len(binary_data) * 2
    assert len(zlib.decompress(compressed_data, wbits=15, bufsize=bufsize)) == len(decompressed_data)
# End program