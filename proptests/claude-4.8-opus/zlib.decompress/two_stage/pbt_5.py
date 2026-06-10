from hypothesis import given, strategies as st, assume
import zlib

# Property 1: The output is always a bytes object.
@given(st.binary(max_size=4096))
def test_zlib_decompress_returns_bytes(original):
    compressed = zlib.compress(original)
    result = zlib.decompress(compressed)
    assert isinstance(result, bytes)


# Property 2: Round-trip with zlib.compress returns the original bytes exactly.
@given(st.binary(max_size=4096))
def test_zlib_decompress_roundtrip(original):
    compressed = zlib.compress(original)
    result = zlib.decompress(compressed)
    assert result == original


# Property 3: Output is independent of the bufsize argument.
@given(
    st.binary(max_size=4096),
    st.integers(min_value=1, max_value=65536),
    st.integers(min_value=1, max_value=65536),
)
def test_zlib_decompress_bufsize_independent(original, bufsize1, bufsize2):
    compressed = zlib.compress(original)
    result1 = zlib.decompress(compressed, zlib.MAX_WBITS, bufsize1)
    result2 = zlib.decompress(compressed, zlib.MAX_WBITS, bufsize2)
    assert result1 == result2 == original


# Property 4: Decompression succeeds when wbits window size >= the one used to compress,
# and the output matches the original.
@given(
    st.binary(max_size=4096),
    st.integers(min_value=8, max_value=15),
    st.data(),
)
def test_zlib_decompress_compatible_wbits(original, comp_wbits, data):
    compressed = zlib.compress(original, wbits=comp_wbits)
    # decompression wbits must be >= compression wbits
    decomp_wbits = data.draw(st.integers(min_value=comp_wbits, max_value=15))
    result = zlib.decompress(compressed, decomp_wbits)
    assert result == original


# Property 5: Invalid / corrupted compressed data raises zlib.error.
@given(st.binary(min_size=1, max_size=4096))
def test_zlib_decompress_invalid_raises(garbage):
    # Ensure this isn't accidentally valid compressed data.
    try:
        zlib.decompress(garbage)
    except zlib.error:
        return  # expected behaviour
    # If no error was raised, the input happened to be valid; skip it.
    assume(False)
# End program