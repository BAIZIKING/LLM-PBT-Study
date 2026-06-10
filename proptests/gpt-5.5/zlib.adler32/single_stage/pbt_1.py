from hypothesis import given, strategies as st
import zlib

# Summary: Generate byte data from a mix of explicit edge cases and random binary
# values, split into two chunks to test running checksums, and pass each value as
# bytes, bytearray, or memoryview to cover bytes-like inputs. Generate starting
# checksum values across the full unsigned 32-bit range, emphasizing boundaries.
# Properties checked: the result is an unsigned 32-bit int; the default starting
# value is equivalent to 1; checksums compose over concatenated chunks; different
# bytes-like representations of the same data give the same checksum; empty input
# preserves the starting value.
@given(st.data())
def test_zlib_adler32(data):
    byte_values = st.one_of(
        st.sampled_from(
            [
                b"",
                b"\x00",
                b"\xff",
                b"hello",
                b"\x00" * 1024,
                b"\xff" * 1024,
                bytes(range(256)),
            ]
        ),
        st.binary(min_size=0, max_size=4096),
    )

    start_values = st.one_of(
        st.sampled_from([0, 1, 2, 0xFFFF, 0x10000, 0xFFFFFFFF]),
        st.integers(min_value=0, max_value=0xFFFFFFFF),
    )

    def as_bytes_like(raw):
        representation = data.draw(st.sampled_from(["bytes", "bytearray", "memoryview"]))
        if representation == "bytes":
            return raw
        if representation == "bytearray":
            return bytearray(raw)
        return memoryview(raw)

    first = data.draw(byte_values)
    second = data.draw(byte_values)
    combined = first + second
    start = data.draw(start_values)

    result = zlib.adler32(as_bytes_like(combined), start)

    assert isinstance(result, int)
    assert 0 <= result <= 0xFFFFFFFF

    assert zlib.adler32(as_bytes_like(combined)) == zlib.adler32(as_bytes_like(combined), 1)

    running = zlib.adler32(as_bytes_like(second), zlib.adler32(as_bytes_like(first), start))
    assert result == running

    assert result == zlib.adler32(as_bytes_like(combined), start)

    assert zlib.adler32(as_bytes_like(b""), start) == start

# End program