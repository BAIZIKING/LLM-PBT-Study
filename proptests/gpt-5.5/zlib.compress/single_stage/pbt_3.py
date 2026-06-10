from hypothesis import given, strategies as st
import zlib

# Summary: Generate bytes from arbitrary binary data, exact edge lengths near small sizes and zlib window boundaries, and highly repeated patterns; generate valid compression levels and all documented valid wbits modes. Check that compression returns bytes, round-trips through zlib.decompress with the same wbits, and uses the expected zlib/gzip wrapper markers when documented.
@given(st.data())
def test_zlib_compress(draw):
    edge_lengths = st.sampled_from([
        0, 1, 2, 3, 8, 9, 15, 16, 31, 32,
        255, 256, 511, 512, 513,
        1023, 1024, 32767, 32768, 32769,
    ])

    repeated_pattern_data = st.builds(
        lambda chunk, n: (chunk * ((n // len(chunk)) + 1))[:n],
        st.binary(min_size=1, max_size=64),
        edge_lengths,
    )

    exact_edge_length_data = edge_lengths.flatmap(
        lambda n: st.binary(min_size=n, max_size=n)
    )

    input_data_strategy = st.one_of(
        st.binary(min_size=0, max_size=65536),
        exact_edge_length_data,
        repeated_pattern_data,
        st.sampled_from([
            b"",
            b"\x00",
            b"\xff",
            b"\x00" * 1024,
            b"\xff" * 1024,
            b"hello world" * 100,
            bytes(range(256)),
        ]),
    )

    level_strategy = st.sampled_from([-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    wbits_strategy = st.sampled_from(
        list(range(9, 16)) +
        [-n for n in range(9, 16)] +
        list(range(25, 32))
    )

    original = draw.draw(input_data_strategy)
    level = draw.draw(level_strategy)
    wbits = draw.draw(wbits_strategy)

    compressed = zlib.compress(original, level=level, wbits=wbits)

    assert isinstance(compressed, bytes)
    assert zlib.decompress(compressed, wbits=wbits) == original

    if 9 <= wbits <= 15:
        assert len(compressed) >= 6
        cmf, flg = compressed[0], compressed[1]
        assert cmf & 0x0F == 8
        assert (cmf >> 4) == wbits - 8
        assert ((cmf << 8) + flg) % 31 == 0

    if 25 <= wbits <= 31:
        assert compressed.startswith(b"\x1f\x8b")
        assert compressed[2] == 8
# End program