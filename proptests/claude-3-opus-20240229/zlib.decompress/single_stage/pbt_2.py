from hypothesis import given, strategies as st
import zlib

# Summary: Generate a wide variety of compressed byte strings to test zlib.decompress
# with different window sizes, compression levels, and formats (zlib vs gzip).
# Properties to test:
# 1. Decompressed data matches original uncompressed data 
# 2. Decompressing with too small a window size raises an error
# 3. Invalid compressed data raises an error
# 4. Unsupported formats raise an error
@given(
    orig_data=st.binary(min_size=0, max_size=1024),
    wbits=st.one_of(
        st.integers(min_value=8, max_value=15), 
        st.integers(min_value=-15, max_value=-8),
        st.integers(min_value=24, max_value=31),
        st.just(0)
    ),
    level=st.integers(min_value=0, max_value=9),
    bufsize=st.integers(min_value=8, max_value=1024)
)
def test_decompress(orig_data, wbits, level, bufsize):
    if wbits == 0:  # only compress with zlib format when wbits=0
        compressed = zlib.compress(orig_data, level=level)  
    elif -15 <= wbits <= -8:  # compress with no header/trailer
        compressed = zlib.compress(orig_data, wbits=wbits-16, level=level)[2:-4]
    elif 24 <= wbits <= 31:  # compress with gzip header/trailer
        compressed = zlib.compress(orig_data, wbits=wbits-16, level=level) 
    else:  # compress with zlib header/trailer
        compressed = zlib.compress(orig_data, wbits=wbits, level=level)

    decomp = zlib.decompress(compressed, wbits=wbits, bufsize=bufsize)
    assert decomp == orig_data  # property 1

    if len(compressed) > 0:
        with pytest.raises(zlib.error):  # property 2
            small_wbits = wbits if wbits < 0 else wbits - 1
            zlib.decompress(compressed, wbits=small_wbits)

    with pytest.raises(zlib.error):  # property 3      
        zlib.decompress(b"invalid data", wbits=wbits) 

    unsupported_bits = st.one_of(
        st.integers(max_value=-16), 
        st.integers(min_value=32, max_value=39),
        st.integers(min_value=16, max_value=23)
    )
    with pytest.raises(ValueError, match="invalid wbits"):  # property 4
        zlib.decompress(compressed, wbits=unsupported_bits)
# End program