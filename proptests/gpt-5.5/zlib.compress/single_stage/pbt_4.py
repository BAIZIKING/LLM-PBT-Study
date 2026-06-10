from hypothesis import given, strategies as st
import zlib

# Summary: Generate valid zlib.compress inputs across edge cases: empty bytes, tiny bytes,
# repeated/patterned bytes, arbitrary binary payloads, all documented compression levels,
# and all documented zlib/raw/gzip wbits ranges.
# Properties: For every documented valid input combination, compression returns bytes,
# and decompression with the matching wbits value round-trips exactly to the original data.
# Gzip-mode outputs should also include the documented gzip magic header.
@given(st.data())
def test_zlib_compress(draw):
    input_data = draw(
        st.one_of(
            st.just(b""),
            st.sampled_from(
                [
                    b"\x00",
                    b"\xff",
                    b"hello world",
                    b"\x00" * 1024,
                    b"\xff" * 1024,
                    bytes(range(256)),
                ]
            ),
            st.binary(min_size=0, max_size=4096),
            st.builds(
                lambda chunk, count: chunk * count,
                st.binary(min_size=1, max_size=16),
                st.integers(min_value=0, max_value=512),
            ),
        ),
        label="input_data",
    )

    level = draw(
        st.sampled_from([-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]),
        label="level",
    )

    wbits = draw(
        st.one_of(
            st.integers(min_value=9, max_value=15),
            st.integers(min_value=-15, max_value=-9),
            st.integers(min_value=25, max_value=31),
        ),
        label="wbits",
    )

    compressed = zlib.compress(input_data, level=level, wbits=wbits)

    assert isinstance(compressed, bytes)
    assert zlib.decompress(compressed, wbits=wbits) == input_data

    if 25 <= wbits <= 31:
        assert compressed.startswith(b"\x1f\x8b")

# End program