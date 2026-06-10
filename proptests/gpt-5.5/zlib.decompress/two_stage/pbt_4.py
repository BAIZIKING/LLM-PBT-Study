from hypothesis import given, strategies as st
import zlib


def _compress_with_wbits(payload, wbits):
    compressor = zlib.compressobj(level=-1, method=zlib.DEFLATED, wbits=wbits)
    return compressor.compress(payload) + compressor.flush()


@given(st.data())
def test_zlib_decompress_zlib_roundtrip(data):
    payload = data.draw(st.binary(max_size=8192))
    compressed = zlib.compress(payload)

    decompressed = zlib.decompress(compressed)

    assert decompressed == payload


@given(st.data())
def test_zlib_decompress_returns_bytes(data):
    payload = data.draw(st.binary(max_size=8192))
    compressed = zlib.compress(payload)

    decompressed = zlib.decompress(compressed)

    assert isinstance(decompressed, bytes)


@given(st.data())
def test_zlib_decompress_bufsize_does_not_change_output(data):
    payload = data.draw(st.binary(max_size=8192))
    window_bits = data.draw(st.integers(min_value=9, max_value=15))
    bufsize_1 = data.draw(st.integers(min_value=1, max_value=8192))
    bufsize_2 = data.draw(st.integers(min_value=1, max_value=8192))
    compressed = _compress_with_wbits(payload, window_bits)

    decompressed_1 = zlib.decompress(compressed, wbits=window_bits, bufsize=bufsize_1)
    decompressed_2 = zlib.decompress(compressed, wbits=window_bits, bufsize=bufsize_2)

    assert decompressed_1 == decompressed_2 == payload


@given(st.data())
def test_zlib_decompress_gzip_roundtrip(data):
    payload = data.draw(st.binary(max_size=8192))
    window_bits = data.draw(st.integers(min_value=9, max_value=15))
    gzip_wbits = 16 + window_bits
    compressed = _compress_with_wbits(payload, gzip_wbits)

    decompressed = zlib.decompress(compressed, wbits=gzip_wbits)

    assert decompressed == payload


@given(st.data())
def test_zlib_decompress_raw_deflate_roundtrip(data):
    payload = data.draw(st.binary(max_size=8192))
    window_bits = data.draw(st.integers(min_value=9, max_value=15))
    raw_wbits = -window_bits
    compressed = _compress_with_wbits(payload, raw_wbits)

    decompressed = zlib.decompress(compressed, wbits=raw_wbits)

    assert decompressed == payload


# End program