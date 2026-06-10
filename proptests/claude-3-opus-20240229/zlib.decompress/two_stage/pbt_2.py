from hypothesis import given, strategies as st
import zlib

@given(st.binary(max_size=1000))
def test_decompress_output_size(data):
    compressed = zlib.compress(data)
    decompressed = zlib.decompress(compressed)
    assert len(decompressed) >= len(compressed)

@given(st.binary(max_size=1000))
def test_compress_decompress_identity(data):
    compressed = zlib.compress(data)
    decompressed = zlib.decompress(compressed)
    assert data == decompressed

@given(st.just(b''))
def test_decompress_empty_string(data):
    compressed_empty = zlib.compress(data)
    for wbits in range(-15, 16):
        assert zlib.decompress(compressed_empty, wbits=wbits) == b''

@given(st.binary(max_size=1000))
def test_decompress_with_header_and_trailer(data):
    for wbits in range(8, 16):
        try:
            compressed = zlib.compress(data, wbits=wbits)
            decompressed = zlib.decompress(compressed, wbits=wbits)
            assert data == decompressed
        except zlib.error:
            pass

@given(st.binary(max_size=1000))
def test_decompress_window_size(data):
    for wbits in range(8, 16):
        window_size = 2 ** wbits
        compressed = zlib.compress(data, wbits=-wbits)
        decompressed = zlib.decompress(compressed, wbits=-wbits)
        assert len(decompressed) <= window_size
# End program