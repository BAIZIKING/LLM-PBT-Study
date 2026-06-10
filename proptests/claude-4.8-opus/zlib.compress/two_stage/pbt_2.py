from hypothesis import given, strategies as st
import zlib

# Property 1: The output is always a bytes object.
@given(
    data=st.binary(max_size=10000),
    level=st.integers(min_value=-1, max_value=9),
)
def test_output_is_bytes(data, level):
    result = zlib.compress(data, level=level)
    assert isinstance(result, bytes)
# End program


# Property 2: Round-trip (compress then decompress) yields original data.
@given(
    data=st.binary(max_size=10000),
    level=st.integers(min_value=-1, max_value=9),
    wbits=st.sampled_from(
        list(range(9, 16))      # zlib header
        + list(range(-15, -8))  # raw stream
        + list(range(25, 32))   # gzip header
    ),
)
def test_round_trip(data, level, wbits):
    compressed = zlib.compress(data, level=level, wbits=wbits)
    decompressed = zlib.decompress(compressed, wbits=wbits)
    assert decompressed == data
# End program


# Property 3: Header/format depends on wbits range.
@given(
    data=st.binary(max_size=10000),
    level=st.integers(min_value=-1, max_value=9),
    wbits=st.sampled_from(
        list(range(9, 16))      # zlib header
        + list(range(-15, -8))  # raw stream (no header)
        + list(range(25, 32))   # gzip header
    ),
)
def test_header_format(data, level, wbits):
    compressed = zlib.compress(data, level=level, wbits=wbits)
    if 9 <= wbits <= 15:
        # zlib header: first byte's low 4 bits == 8 (deflate), and the
        # two-byte header is a multiple of 31.
        assert len(compressed) >= 2
        cmf, flg = compressed[0], compressed[1]
        assert (cmf & 0x0F) == 8
        assert ((cmf << 8) | flg) % 31 == 0
    elif 25 <= wbits <= 31:
        # gzip header: starts with magic bytes 0x1f 0x8b and method 0x08.
        assert len(compressed) >= 3
        assert compressed[0] == 0x1F
        assert compressed[1] == 0x8B
        assert compressed[2] == 0x08
    else:
        # Raw stream: must NOT start with zlib or gzip headers.
        if len(compressed) >= 2:
            assert not (compressed[0] == 0x1F and compressed[1] == 0x8B)
# End program


# Property 4: Output is deterministic for the same arguments.
@given(
    data=st.binary(max_size=10000),
    level=st.integers(min_value=-1, max_value=9),
    wbits=st.sampled_from(
        list(range(9, 16))
        + list(range(-15, -8))
        + list(range(25, 32))
    ),
)
def test_deterministic(data, level, wbits):
    first = zlib.compress(data, level=level, wbits=wbits)
    second = zlib.compress(data, level=level, wbits=wbits)
    assert first == second
# End program


# Property 5: Higher compression levels produce output <= lower levels,
# and level 0 produces the largest output.
@given(
    data=st.binary(max_size=10000),
)
def test_level_monotonicity(data):
    size0 = len(zlib.compress(data, level=0))
    size1 = len(zlib.compress(data, level=1))
    size9 = len(zlib.compress(data, level=9))
    # level 0 (no compression) is the largest
    assert size0 >= size1
    assert size0 >= size9
    # level 9 compresses at least as well as level 1
    assert size9 <= size1
# End program