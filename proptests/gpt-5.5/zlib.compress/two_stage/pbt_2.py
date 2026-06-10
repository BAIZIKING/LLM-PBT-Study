from hypothesis import given, strategies as st
import zlib

VALID_LEVELS = st.integers(min_value=-1, max_value=9)
VALID_WBITS = st.one_of(
    st.integers(min_value=9, max_value=15),
    st.integers(min_value=-15, max_value=-9),
    st.integers(min_value=25, max_value=31),
)
SMALL_BYTES = st.binary(max_size=100_000)


@given(st.data())
def test_zlib_compress_returns_bytes(data):
    raw = data.draw(SMALL_BYTES)
    level = data.draw(VALID_LEVELS)
    wbits = data.draw(VALID_WBITS)

    compressed = zlib.compress(raw, level=level, wbits=wbits)

    assert isinstance(compressed, bytes)


@given(st.data())
def test_zlib_compress_round_trips_with_matching_wbits(data):
    raw = data.draw(SMALL_BYTES)
    level = data.draw(VALID_LEVELS)
    wbits = data.draw(VALID_WBITS)

    compressed = zlib.compress(raw, level=level, wbits=wbits)
    decompressed = zlib.decompress(compressed, wbits=wbits)

    assert decompressed == raw


@given(st.data())
def test_zlib_compress_is_deterministic(data):
    raw = data.draw(SMALL_BYTES)
    level = data.draw(VALID_LEVELS)
    wbits = data.draw(VALID_WBITS)

    compressed_1 = zlib.compress(raw, level=level, wbits=wbits)
    compressed_2 = zlib.compress(raw, level=level, wbits=wbits)

    assert compressed_1 == compressed_2


@given(st.data())
def test_zlib_compress_positive_wbits_has_valid_zlib_wrapper(data):
    raw = data.draw(SMALL_BYTES)
    level = data.draw(VALID_LEVELS)
    wbits = data.draw(st.integers(min_value=9, max_value=15))

    compressed = zlib.compress(raw, level=level, wbits=wbits)

    assert len(compressed) >= 6
    cmf = compressed[0]
    flg = compressed[1]
    assert cmf & 0x0F == 8
    assert ((cmf << 8) + flg) % 31 == 0
    assert zlib.decompress(compressed, wbits=wbits) == raw
    assert int.from_bytes(compressed[-4:], "big") == zlib.adler32(raw) & 0xFFFFFFFF


@given(st.data())
def test_zlib_compress_gzip_wbits_has_valid_gzip_wrapper(data):
    raw = data.draw(SMALL_BYTES)
    level = data.draw(VALID_LEVELS)
    wbits = data.draw(st.integers(min_value=25, max_value=31))

    compressed = zlib.compress(raw, level=level, wbits=wbits)

    assert len(compressed) >= 18
    assert compressed[:2] == b"\x1f\x8b"
    assert compressed[2] == 8
    assert zlib.decompress(compressed, wbits=wbits) == raw
    assert int.from_bytes(compressed[-8:-4], "little") == zlib.crc32(raw) & 0xFFFFFFFF
    assert int.from_bytes(compressed[-4:], "little") == len(raw) & 0xFFFFFFFF


# End program