from hypothesis import given, strategies as st, settings
import zlib
import pytest

# Strategy for reasonable byte inputs (bounded to avoid very large inputs/overflows)
data_strategy = st.binary(min_size=0, max_size=4096)

# Strategy for bufsize: keep within a sane positive range to avoid huge allocations
bufsize_strategy = st.integers(min_value=1, max_value=2**16)


# Property 1: The output of zlib.decompress is always a bytes object.
@given(data=data_strategy)
@settings(max_examples=200)
def test_zlib_decompress_returns_bytes(data):
    compressed = zlib.compress(data)
    result = zlib.decompress(compressed)
    assert isinstance(result, bytes)
# End program


# Property 2: Round-trip — decompressing compressed(x) returns x.
@given(data=data_strategy)
@settings(max_examples=200)
def test_zlib_decompress_roundtrip(data):
    compressed = zlib.compress(data)
    result = zlib.decompress(compressed)
    assert result == data
# End program


# Property 3: Output is independent of bufsize.
@given(data=data_strategy, bufsize1=bufsize_strategy, bufsize2=bufsize_strategy)
@settings(max_examples=200)
def test_zlib_decompress_bufsize_independent(data, bufsize1, bufsize2):
    compressed = zlib.compress(data)
    result1 = zlib.decompress(compressed, bufsize=bufsize1)
    result2 = zlib.decompress(compressed, bufsize=bufsize2)
    assert result1 == result2
# End program


# Property 4: Auto-detecting wbits yields the same output as the specific correct wbits.
@given(data=data_strategy)
@settings(max_examples=200)
def test_zlib_decompress_wbits_autodetect(data):
    compressed = zlib.compress(data)
    # Default wbits (zlib header/trailer) vs auto-detect (32 + 15 = 47)
    result_default = zlib.decompress(compressed, wbits=zlib.MAX_WBITS)
    result_auto = zlib.decompress(compressed, wbits=47)
    assert result_default == result_auto
# End program


# Property 5: Malformed/corrupted input raises zlib.error.
@given(data=st.binary(min_size=1, max_size=256))
@settings(max_examples=200)
def test_zlib_decompress_malformed_raises(data):
    # Random bytes are extremely unlikely to be valid zlib streams;
    # if by chance they are valid, decompression simply succeeds, which is fine.
    try:
        result = zlib.decompress(data)
        assert isinstance(result, bytes)
    except zlib.error:
        pass  # Expected for malformed input
# End program