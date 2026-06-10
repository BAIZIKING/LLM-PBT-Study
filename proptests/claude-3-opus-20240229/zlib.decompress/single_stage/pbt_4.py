from hypothesis import given, strategies as st
import zlib

# Summary: Generate a wide variety of compressed data to test zlib.decompress
# - Generate random bytes of various lengths to compress 
# - Use different compression levels
# - Use different window sizes (wbits) including special values like 0 and +32
# - Sometimes include zlib/gzip headers and trailers, sometimes use raw streams
# - Fuzz bufsize to test different initial output buffer sizes
# Check that:
# - Decompressing the compressed data gives back the original input data
# - Decompressing corrupt data or with incorrect wbits raises an error
# - Decompressing with too small a wbits value raises an error
# - Varying bufsize doesn't impact the decompressed output
@given(
    orig_data=st.binary(min_size=0, max_size=1024), 
    wbits=st.one_of(
        st.integers(min_value=8, max_value=15),
        st.integers(min_value=24, max_value=31),
        st.integers(min_value=40, max_value=47),
        st.just(0)
    ),
    header=st.booleans(),
    level=st.integers(min_value=0, max_value=9),
    bufsize=st.integers(min_value=1)
)
def test_zlib_decompress(orig_data, wbits, header, level, bufsize):
    if header:
        compressed = zlib.compress(orig_data, level)
    else:
        compressed = zlib.compress(orig_data, level)[2:-4]

    if 40 <= wbits <= 47:
        if header:
            fmt = "gzip"
        else:
            fmt = "auto"
    elif 24 <= wbits <= 31:
        fmt = "gzip"
    else:
        fmt = "zlib"

    decompressed = zlib.decompress(compressed, wbits=wbits, bufsize=bufsize)
    assert decompressed == orig_data

    if not header:
        too_small_wbits = -wbits-1
        with pytest.raises(zlib.error):
            zlib.decompress(compressed, wbits=too_small_wbits, bufsize=bufsize)

    corrupt_compressed = bytearray(compressed)
    corrupt_compressed[len(corrupt_compressed)//2] ^= 0xff
    with pytest.raises(zlib.error):
        zlib.decompress(corrupt_compressed, wbits=wbits)
# End program