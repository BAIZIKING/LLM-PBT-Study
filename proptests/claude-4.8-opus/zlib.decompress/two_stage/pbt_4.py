from hypothesis import given, settings, strategies as st
import zlib

# Strategy for reasonable-sized byte inputs to avoid very large inputs / slow compression.
data_strategy = st.binary(min_size=0, max_size=4096)

# Valid window-size logarithms for zlib format.
wbits_zlib = st.integers(min_value=8, max_value=15)


# Property 1: The output is always a bytes object.
@given(data_strategy)
@settings(deadline=None)
def test_output_is_bytes(original):
    compressed = zlib.compress(original)
    result = zlib.decompress(compressed)
    assert isinstance(result, bytes)
# End program


# Property 2: Round-trip — decompress(compress(x)) == x.
@given(data_strategy)
@settings(deadline=None)
def test_round_trip(original):
    compressed = zlib.compress(original)
    result = zlib.decompress(compressed)
    assert result == original
# End program


# Property 3: A wbits >= original compression window succeeds and equals original;
# a strictly smaller window may raise zlib.error.
@given(data_strategy, st.integers(min_value=9, max_value=15), st.data())
@settings(deadline=None)
def test_window_size_constraint(original, comp_wbits, data):
    compressor = zlib.compressobj(level=6, wbits=comp_wbits)
    compressed = compressor.compress(original) + compressor.flush()

    # Larger-or-equal window must succeed and round-trip.
    larger = data.draw(st.integers(min_value=comp_wbits, max_value=15))
    assert zlib.decompress(compressed, larger) == original

    # Strictly smaller window: should either succeed (rare) or raise zlib.error.
    smaller = data.draw(st.integers(min_value=8, max_value=comp_wbits - 1))
    try:
        result = zlib.decompress(compressed, smaller)
        assert result == original
    except zlib.error:
        pass
# End program


# Property 4: Output is independent of bufsize.
@given(
    data_strategy,
    st.integers(min_value=1, max_value=65536),
    st.integers(min_value=1, max_value=65536),
)
@settings(deadline=None)
def test_bufsize_independence(original, bufsize_a, bufsize_b):
    compressed = zlib.compress(original)
    result_a = zlib.decompress(compressed, zlib.MAX_WBITS, bufsize_a)
    result_b = zlib.decompress(compressed, zlib.MAX_WBITS, bufsize_b)
    assert result_a == result_b
# End program


# Property 5: Auto-detect and format-specific wbits agree with the default for
# both zlib and gzip formats.
@given(data_strategy)
@settings(deadline=None)
def test_format_detection_consistency(original):
    # zlib format
    zlib_data = zlib.compress(original)
    default_out = zlib.decompress(zlib_data)
    zlib_specific = zlib.decompress(zlib_data, 15)
    zlib_auto = zlib.decompress(zlib_data, 47)
    assert default_out == original
    assert zlib_specific == original
    assert zlib_auto == original

    # gzip format
    gzip_comp = zlib.compressobj(wbits=16 + 15)
    gzip_data = gzip_comp.compress(original) + gzip_comp.flush()
    gzip_specific = zlib.decompress(gzip_data, 16 + 15)
    gzip_auto = zlib.decompress(gzip_data, 47)
    assert gzip_specific == original
    assert gzip_auto == original
# End program