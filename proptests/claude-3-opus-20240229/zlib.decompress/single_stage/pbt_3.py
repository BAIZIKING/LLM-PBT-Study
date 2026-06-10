from hypothesis import given, strategies as st
import zlib

# Summary: Generate a wide variety of compressed byte strings to test zlib.decompress
# - Generate random byte strings of varying lengths
# - Randomly select window sizes (wbits) covering the allowed ranges 
# - Randomly add zlib/gzip headers and trailers based on wbits
# - Check that decompress output matches original uncompressed data
# - Check that invalid inputs raise error exceptions
@given(st.data())
def test_zlib_decompress(data):
    # Generate random uncompressed data 
    original = data.draw(st.binary(min_size=0, max_size=1024))
    
    # Generate random wbits value
    wbits = data.draw(st.one_of(
        st.integers(min_value=8, max_value=15), 
        st.integers(min_value=-15, max_value=-8),
        st.integers(min_value=24, max_value=31),
        st.integers(min_value=40, max_value=47),
        st.just(0)
    ))

    # Only add header if wbits is positive
    if wbits > 0:
        # Add zlib header if 8 <= wbits <= 15
        if wbits <= 15: 
            compressed = zlib.compress(original, wbits)
        # Add gzip header if 24 <= wbits <= 31
        else:
            compressed = zlib.compress(original, wbits-16)
    # Otherwise, compress without header
    else:
        compressed = zlib.compress(original, -wbits)

    # Test decompress with valid input
    decompressed = zlib.decompress(compressed, wbits)
    assert decompressed == original

    # Test invalid wbits raises error
    if wbits >= 0:
        with pytest.raises(zlib.error):
            zlib.decompress(compressed, wbits-16)
    else:
        with pytest.raises(zlib.error):  
            zlib.decompress(compressed, -wbits-1)

    # Test corrupted data raises error  
    corrupted = compressed[:-1]
    with pytest.raises(zlib.error):
        zlib.decompress(corrupted, wbits)
# End program