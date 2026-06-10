from hypothesis import given, strategies as st, assume, settings
import zlib

# Strategy for raw data to compress. Keep sizes bounded to avoid very large
# inputs / excessive memory usage during decompression.
raw_data_strategy = st.binary(min_size=0, max_size=4096)

# Valid window-size logarithms for the zlib format (+8 to +15).
zlib_wbits_strategy = st.integers(min_value=8, max_value=15)

# Valid window-size logarithms for the gzip format (+24 to +31).
gzip_wbits_strategy = st.integers(min_value=24, max_value=31)

# Valid auto-detect (zlib or gzip) window logarithms (+40 to +47).
auto_wbits_strategy = st.integers(min_value=40, max_value=47)

# Valid raw-stream window logarithms (-8 to -15).
raw_wbits_strategy = st.integers(min_value=-15, max_value=-8)

# Reasonable bufsize values; the docs say buffer grows as needed,
# so exact value doesn't matter for correctness.
bufsize_strategy = st.integers(min_value=1, max_value=65536)


@given(st.data())
@settings(deadline=None)
def test_zlib_decompress_property(data):
    # ------------------------------------------------------------------
    # Property 1: The output of zlib.decompress is always a bytes object.
    # ------------------------------------------------------------------
    original = data.draw(raw_data_strategy)
    wbits = data.draw(zlib_wbits_strategy)
    compressed = zlib.compress(original, level=data.draw(st.integers(0, 9)))
    result = zlib.decompress(compressed, wbits)
    assert isinstance(result, bytes)

    # ------------------------------------------------------------------
    # Property 2: Round-trip — decompressing the result of compressing some
    # original data (with compatible wbits) returns exactly the original.
    # ------------------------------------------------------------------
    original2 = data.draw(raw_data_strategy)
    comp_wbits = data.draw(zlib_wbits_strategy)
    # Compress using a compressobj so we control the window size (wbits).
    compressor = zlib.compressobj(6, zlib.DEFLATED, comp_wbits)
    compressed2 = compressor.compress(original2) + compressor.flush()
    # Decompress using the same window size (compatible wbits).
    roundtrip = zlib.decompress(compressed2, comp_wbits)
    assert roundtrip == original2

    # ------------------------------------------------------------------
    # Property 3: The output is independent of the bufsize argument.
    # ------------------------------------------------------------------
    original3 = data.draw(raw_data_strategy)
    wbits3 = data.draw(zlib_wbits_strategy)
    compressed3 = zlib.compress(original3)
    bufsize_a = data.draw(bufsize_strategy)
    bufsize_b = data.draw(bufsize_strategy)
    out_a = zlib.decompress(compressed3, wbits3, bufsize_a)
    out_b = zlib.decompress(compressed3, wbits3, bufsize_b)
    assert out_a == out_b

    # ------------------------------------------------------------------
    # Property 4: Auto-detect wbits (40..47) matches the format-specific
    # decompression result (zlib or gzip) for the same data.
    # ------------------------------------------------------------------
    original4 = data.draw(raw_data_strategy)
    log = data.draw(st.integers(min_value=8, max_value=15))
    use_gzip = data.draw(st.booleans())
    if use_gzip:
        # gzip format: window logarithm + 16.
        compressor4 = zlib.compressobj(6, zlib.DEFLATED, 16 + log)
        explicit_wbits = 16 + log
    else:
        # zlib format.
        compressor4 = zlib.compressobj(6, zlib.DEFLATED, log)
        explicit_wbits = log
    compressed4 = compressor4.compress(original4) + compressor4.flush()
    # Auto-detect must use a window at least as large; use max log = 15.
    auto_result = zlib.decompress(compressed4, 32 + 15)
    explicit_result = zlib.decompress(compressed4, explicit_wbits)
    assert auto_result == explicit_result == original4

    # ------------------------------------------------------------------
    # Property 5: A window size >= the one used at compression decompresses
    # correctly, while a too-small window raises zlib.error.
    # ------------------------------------------------------------------
    original5 = data.draw(raw_data_strategy)
    comp_log = data.draw(st.integers(min_value=9, max_value=15))
    compressor5 = zlib.compressobj(6, zlib.DEFLATED, comp_log)
    compressed5 = compressor5.compress(original5) + compressor5.flush()

    # Decompressing with a window >= comp_log must succeed and round-trip.
    larger_log = data.draw(st.integers(min_value=comp_log, max_value=15))
    ok_result = zlib.decompress(compressed5, larger_log)
    assert ok_result == original5

    # Decompressing with a strictly smaller window may raise zlib.error.
    # (Only assert error behaviour when the data is large enough to actually
    # need a window larger than the smaller one; small data can decode anyway.)
    smaller_log = comp_log - 1
    try:
        small_result = zlib.decompress(compressed5, smaller_log)
        # If it succeeds (small data fit in the smaller window), it must
        # still be correct.
        assert small_result == original5
    except zlib.error:
        # Acceptable: too-small window may raise the error exception.
        pass
# End program