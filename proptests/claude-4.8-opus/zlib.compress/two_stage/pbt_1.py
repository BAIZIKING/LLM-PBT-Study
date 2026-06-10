from hypothesis import given, strategies as st, assume
import zlib

# Bounded input size to avoid very large inputs and potential overflows
data_strategy = st.binary(min_size=0, max_size=4096)
level_strategy = st.integers(min_value=-1, max_value=9)

zlib_wbits = st.integers(min_value=9, max_value=15)
raw_wbits = st.integers(min_value=-15, max_value=-9)
gzip_wbits = st.integers(min_value=25, max_value=31)
all_wbits = st.one_of(zlib_wbits, raw_wbits, gzip_wbits)


# Property 1: The output is always a bytes object.
@given(st.data())
def test_zlib_compress_output_is_bytes(data):
    input_data = data.draw(data_strategy)
    level = data.draw(level_strategy)
    wbits = data.draw(all_wbits)
    result = zlib.compress(input_data, level=level, wbits=wbits)
    assert isinstance(result, bytes)
# End program


# Property 2: Round-trip — decompressing the output yields the original input.
@given(st.data())
def test_zlib_compress_round_trip(data):
    input_data = data.draw(data_strategy)
    level = data.draw(level_strategy)
    wbits = data.draw(all_wbits)
    compressed = zlib.compress(input_data, level=level, wbits=wbits)
    decompressed = zlib.decompress(compressed, wbits=wbits)
    assert decompressed == input_data
# End program


# Property 3: Header format matches the wbits range.
@given(st.data())
def test_zlib_compress_header_format(data):
    input_data = data.draw(data_strategy)
    level = data.draw(level_strategy)

    # zlib format: should be decompressible with a positive wbits
    zw = data.draw(zlib_wbits)
    zlib_out = zlib.compress(input_data, level=level, wbits=zw)
    assert zlib.decompress(zlib_out, wbits=zw) == input_data
    # gzip output (16+) should NOT start with a valid zlib header decode at default
    # but zlib output should be decodable with standard zlib (wbits=15)
    assert zlib.decompress(zlib_out, wbits=15) == input_data

    # gzip format: starts with the gzip magic bytes 0x1f 0x8b
    gw = data.draw(gzip_wbits)
    gzip_out = zlib.compress(input_data, level=level, wbits=gw)
    assert gzip_out[:2] == b"\x1f\x8b"

    # raw format: no zlib header/trailer; decompressible only with negative wbits
    rw = data.draw(raw_wbits)
    raw_out = zlib.compress(input_data, level=level, wbits=rw)
    assert zlib.decompress(raw_out, wbits=rw) == input_data
# End program


# Property 4: Level 0 (no compression) is never smaller than higher levels.
@given(st.data())
def test_zlib_compress_level_size_monotonic(data):
    input_data = data.draw(data_strategy)
    wbits = data.draw(all_wbits)
    size_level0 = len(zlib.compress(input_data, level=0, wbits=wbits))
    higher_level = data.draw(st.integers(min_value=1, max_value=9))
    size_higher = len(zlib.compress(input_data, level=higher_level, wbits=wbits))
    assert size_level0 >= size_higher
# End program


# Property 5: Compression is deterministic for identical arguments.
@given(st.data())
def test_zlib_compress_deterministic(data):
    input_data = data.draw(data_strategy)
    level = data.draw(level_strategy)
    wbits = data.draw(all_wbits)
    result_a = zlib.compress(input_data, level=level, wbits=wbits)
    result_b = zlib.compress(input_data, level=level, wbits=wbits)
    assert result_a == result_b
# End program