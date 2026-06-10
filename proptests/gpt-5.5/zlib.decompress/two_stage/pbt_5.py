from hypothesis import given, strategies as st
import zlib

@given(st.data())
def test_zlib_decompress_returns_bytes(data):
    payload = data.draw(st.binary(max_size=8192))
    level = data.draw(st.integers(min_value=0, max_value=9))
    wbits = data.draw(st.integers(min_value=9, max_value=15))
    fmt = data.draw(st.sampled_from(["zlib", "raw", "gzip"]))

    if fmt == "zlib":
        compressor = zlib.compressobj(level=level, method=zlib.DEFLATED, wbits=wbits)
        compressed = compressor.compress(payload) + compressor.flush()
        decompressed = zlib.decompress(compressed, wbits=wbits)
    elif fmt == "raw":
        compressor = zlib.compressobj(level=level, method=zlib.DEFLATED, wbits=-wbits)
        compressed = compressor.compress(payload) + compressor.flush()
        decompressed = zlib.decompress(compressed, wbits=-wbits)
    else:
        compressor = zlib.compressobj(level=level, method=zlib.DEFLATED, wbits=16 + wbits)
        compressed = compressor.compress(payload) + compressor.flush()
        decompressed = zlib.decompress(compressed, wbits=16 + wbits)

    assert isinstance(decompressed, bytes)


@given(st.data())
def test_zlib_decompress_zlib_roundtrip(data):
    payload = data.draw(st.binary(max_size=8192))
    level = data.draw(st.integers(min_value=0, max_value=9))
    wbits = data.draw(st.integers(min_value=9, max_value=15))

    compressor = zlib.compressobj(level=level, method=zlib.DEFLATED, wbits=wbits)
    compressed = compressor.compress(payload) + compressor.flush()

    assert zlib.decompress(compressed, wbits=wbits) == payload


@given(st.data())
def test_zlib_decompress_raw_roundtrip(data):
    payload = data.draw(st.binary(max_size=8192))
    level = data.draw(st.integers(min_value=0, max_value=9))
    wbits = data.draw(st.integers(min_value=9, max_value=15))

    compressor = zlib.compressobj(level=level, method=zlib.DEFLATED, wbits=-wbits)
    compressed = compressor.compress(payload) + compressor.flush()

    assert zlib.decompress(compressed, wbits=-wbits) == payload


@given(st.data())
def test_zlib_decompress_gzip_roundtrip(data):
    payload = data.draw(st.binary(max_size=8192))
    level = data.draw(st.integers(min_value=0, max_value=9))
    wbits = data.draw(st.integers(min_value=9, max_value=15))

    compressor = zlib.compressobj(level=level, method=zlib.DEFLATED, wbits=16 + wbits)
    compressed = compressor.compress(payload) + compressor.flush()

    assert zlib.decompress(compressed, wbits=16 + wbits) == payload


@given(st.data())
def test_zlib_decompress_bufsize_does_not_change_output(data):
    payload = data.draw(st.binary(max_size=8192))
    level = data.draw(st.integers(min_value=0, max_value=9))
    wbits = data.draw(st.integers(min_value=9, max_value=15))
    bufsize_1 = data.draw(st.integers(min_value=1, max_value=65536))
    bufsize_2 = data.draw(st.integers(min_value=1, max_value=65536))
    fmt = data.draw(st.sampled_from(["zlib", "raw", "gzip"]))

    if fmt == "zlib":
        compressor = zlib.compressobj(level=level, method=zlib.DEFLATED, wbits=wbits)
        compressed = compressor.compress(payload) + compressor.flush()
        decompress_wbits = wbits
    elif fmt == "raw":
        compressor = zlib.compressobj(level=level, method=zlib.DEFLATED, wbits=-wbits)
        compressed = compressor.compress(payload) + compressor.flush()
        decompress_wbits = -wbits
    else:
        compressor = zlib.compressobj(level=level, method=zlib.DEFLATED, wbits=16 + wbits)
        compressed = compressor.compress(payload) + compressor.flush()
        decompress_wbits = 16 + wbits

    output_1 = zlib.decompress(compressed, wbits=decompress_wbits, bufsize=bufsize_1)
    output_2 = zlib.decompress(compressed, wbits=decompress_wbits, bufsize=bufsize_2)

    assert output_1 == output_2 == payload
# End program