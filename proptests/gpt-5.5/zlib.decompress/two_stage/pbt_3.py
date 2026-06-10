from hypothesis import given, strategies as st
import zlib

def _compress(data, wbits, level=6):
    compressor = zlib.compressobj(level=level, method=zlib.DEFLATED, wbits=wbits)
    return compressor.compress(data) + compressor.flush()

@given(st.data())
def test_zlib_decompress_returns_bytes_for_successful_inputs(data):
    payload = data.draw(st.binary(max_size=8192))
    window_bits = data.draw(st.integers(min_value=9, max_value=15))
    level = data.draw(st.integers(min_value=0, max_value=9))
    fmt = data.draw(st.sampled_from(["zlib", "raw", "gzip", "auto_zlib", "auto_gzip"]))

    if fmt == "zlib":
        compressed = _compress(payload, window_bits, level)
        decompress_wbits = window_bits
    elif fmt == "raw":
        compressed = _compress(payload, -window_bits, level)
        decompress_wbits = -window_bits
    elif fmt == "gzip":
        compressed = _compress(payload, 16 + window_bits, level)
        decompress_wbits = 16 + window_bits
    elif fmt == "auto_zlib":
        compressed = _compress(payload, window_bits, level)
        decompress_wbits = 32 + window_bits
    else:
        compressed = _compress(payload, 16 + window_bits, level)
        decompress_wbits = 32 + window_bits

    result = zlib.decompress(compressed, wbits=decompress_wbits)
    assert isinstance(result, bytes)

@given(st.data())
def test_zlib_decompress_zlib_round_trip_returns_original_bytes(data):
    payload = data.draw(st.binary(max_size=8192))
    window_bits = data.draw(st.integers(min_value=9, max_value=15))
    level = data.draw(st.integers(min_value=0, max_value=9))

    compressed = _compress(payload, window_bits, level)
    result = zlib.decompress(compressed, wbits=window_bits)

    assert result == payload

@given(st.data())
def test_zlib_decompress_bufsize_does_not_change_output(data):
    payload = data.draw(st.binary(max_size=8192))
    window_bits = data.draw(st.integers(min_value=9, max_value=15))
    level = data.draw(st.integers(min_value=0, max_value=9))
    bufsize_a = data.draw(st.integers(min_value=1, max_value=16384))
    bufsize_b = data.draw(st.integers(min_value=1, max_value=16384))

    compressed = _compress(payload, window_bits, level)

    result_a = zlib.decompress(compressed, wbits=window_bits, bufsize=bufsize_a)
    result_b = zlib.decompress(compressed, wbits=window_bits, bufsize=bufsize_b)

    assert result_a == result_b == payload

@given(st.data())
def test_zlib_decompress_gzip_round_trip_returns_original_bytes(data):
    payload = data.draw(st.binary(max_size=8192))
    window_bits = data.draw(st.integers(min_value=9, max_value=15))
    level = data.draw(st.integers(min_value=0, max_value=9))

    compressed = _compress(payload, 16 + window_bits, level)
    result = zlib.decompress(compressed, wbits=16 + window_bits)

    assert result == payload

@given(st.data())
def test_zlib_decompress_auto_detect_matches_explicit_format(data):
    payload = data.draw(st.binary(max_size=8192))
    window_bits = data.draw(st.integers(min_value=9, max_value=15))
    level = data.draw(st.integers(min_value=0, max_value=9))
    use_gzip = data.draw(st.booleans())

    if use_gzip:
        compressed = _compress(payload, 16 + window_bits, level)
        explicit_wbits = 16 + window_bits
    else:
        compressed = _compress(payload, window_bits, level)
        explicit_wbits = window_bits

    explicit_result = zlib.decompress(compressed, wbits=explicit_wbits)
    auto_result = zlib.decompress(compressed, wbits=32 + window_bits)

    assert auto_result == explicit_result == payload

# End program