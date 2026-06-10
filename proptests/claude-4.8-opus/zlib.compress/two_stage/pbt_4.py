from hypothesis import given, strategies as st
import zlib

data_strategy = st.binary(min_size=0, max_size=4096)
level_strategy = st.integers(min_value=-1, max_value=9)

zlib_wbits = st.integers(min_value=9, max_value=15)
raw_wbits = st.integers(min_value=-15, max_value=-9)
gzip_wbits = st.integers(min_value=25, max_value=31)
all_wbits = st.one_of(zlib_wbits, raw_wbits, gzip_wbits)


@given(st.data())
def test_zlib_compress_roundtrip(draw):
    # Property 1: decompression with matching wbits recovers original input.
    data = draw.draw(data_strategy)
    level = draw.draw(level_strategy)
    wbits = draw.draw(all_wbits)
    compressed = zlib.compress(data, level, wbits)
    assert zlib.decompress(compressed, wbits) == data


@given(st.data())
def test_zlib_compress_output_type(draw):
    # Property 2: output is always a bytes object.
    data = draw.draw(data_strategy)
    level = draw.draw(level_strategy)
    wbits = draw.draw(all_wbits)
    compressed = zlib.compress(data, level, wbits)
    assert isinstance(compressed, bytes)


@given(st.data())
def test_zlib_compress_header_depends_on_wbits(draw):
    # Property 3: header/format depends on the wbits range.
    data = draw.draw(data_strategy)
    level = draw.draw(level_strategy)

    # zlib format (+9..+15): standard zlib header; can be decompressed with wbits 15.
    wbits_zlib = draw.draw(zlib_wbits)
    out_zlib = zlib.compress(data, level, wbits_zlib)
    assert zlib.decompress(out_zlib) == data  # default wbits parses zlib header

    # gzip format (+25..+31): output starts with gzip magic bytes 0x1f 0x8b.
    wbits_gzip = draw.draw(gzip_wbits)
    out_gzip = zlib.compress(data, level, wbits_gzip)
    assert out_gzip[:2] == b"\x1f\x8b"

    # raw format (-9..-15): no zlib/gzip header; not parseable as zlib stream.
    wbits_raw = draw.draw(raw_wbits)
    out_raw = zlib.compress(data, level, wbits_raw)
    # Raw stream has no gzip magic and must be decompressed with negative wbits.
    assert out_raw[:2] != b"\x1f\x8b"
    assert zlib.decompress(out_raw, wbits_raw) == data


@given(st.data())
def test_zlib_compress_empty_input(draw):
    # Property 4: empty input yields valid bytes that decompress back to b"".
    level = draw.draw(level_strategy)
    wbits = draw.draw(all_wbits)
    compressed = zlib.compress(b"", level, wbits)
    assert isinstance(compressed, bytes)
    assert zlib.decompress(compressed, wbits) == b""


@given(st.data())
def test_zlib_compress_default_level_equals_six(draw):
    # Property 5: level=-1 produces the same output as level=6 (same data/wbits).
    data = draw.draw(data_strategy)
    wbits = draw.draw(all_wbits)
    assert zlib.compress(data, -1, wbits) == zlib.compress(data, 6, wbits)
# End program