from hypothesis import given, strategies as st
import zlib

# Property 1: The output is always a bytes object.
@given(
    data=st.binary(max_size=4096),
    level=st.integers(min_value=-1, max_value=9),
)
def test_zlib_compress_returns_bytes(data, level):
    result = zlib.compress(data, level)
    assert isinstance(result, bytes)
# End program


# Property 2: Decompressing the output returns the original input data exactly (round-trip).
@given(
    data=st.binary(max_size=4096),
    level=st.integers(min_value=-1, max_value=9),
    wbits=st.integers(min_value=9, max_value=15)
    | st.integers(min_value=-15, max_value=-9)
    | st.integers(min_value=25, max_value=31),
)
def test_zlib_compress_roundtrip(data, level, wbits):
    compressed = zlib.compress(data, level, wbits)
    decompressed = zlib.decompress(compressed, wbits)
    assert decompressed == data
# End program


# Property 3: When wbits is +9 to +15, the output has a valid zlib header.
@given(
    data=st.binary(max_size=4096),
    level=st.integers(min_value=-1, max_value=9),
    wbits=st.integers(min_value=9, max_value=15),
)
def test_zlib_compress_zlib_header(data, level, wbits):
    result = zlib.compress(data, level, wbits)
    assert len(result) >= 2
    # Low 4 bits of first byte equal 8 (deflate method).
    assert (result[0] & 0x0F) == 8
    # The two-byte header is a multiple of 31.
    header = (result[0] << 8) | result[1]
    assert header % 31 == 0
# End program


# Property 4: When wbits is +25 to +31, the output begins with gzip magic bytes.
@given(
    data=st.binary(max_size=4096),
    level=st.integers(min_value=-1, max_value=9),
    wbits=st.integers(min_value=25, max_value=31),
)
def test_zlib_compress_gzip_header(data, level, wbits):
    result = zlib.compress(data, level, wbits)
    assert len(result) >= 2
    assert result[0] == 0x1F
    assert result[1] == 0x8B
# End program


# Property 5: Higher compression level produces output <= size of lower level
# for sufficiently compressible inputs.
@given(
    data=st.binary(min_size=100, max_size=8192),
)
def test_zlib_compress_level_monotonicity(data):
    # Make the input highly compressible by repeating it.
    compressible = data * 8
    low = zlib.compress(compressible, 1)
    high = zlib.compress(compressible, 9)
    assert len(high) <= len(low)
# End program