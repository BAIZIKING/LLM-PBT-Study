from hypothesis import given, strategies as st
import zlib

# Define a strategy for generating data within a reasonable size limit to avoid overflows
data_strategy = st.binary(max_size=1024)

@given(data_strategy)
def test_adler32_empty_input(data):
    assert zlib.adler32(b"") == 1
    assert zlib.adler32(data, 1) == zlib.adler32(b"" + data, 1)

@given(data_strategy, st.integers())
def test_adler32_initial_value(data, initial_value):
    assert zlib.adler32(b"", initial_value) == initial_value

@given(data_strategy, st.integers())
def test_adler32_deterministic(data, initial_value):
    first_checksum = zlib.adler32(data, initial_value)
    second_checksum = zlib.adler32(data, initial_value)
    assert first_checksum == second_checksum

@given(data_strategy, data_strategy, st.integers())
def test_adler32_order_independence(data1, data2, initial_value):
    checksum1 = zlib.adler32(data1 + data2, initial_value)
    checksum2 = zlib.adler32(data2 + data1, initial_value)
    assert checksum1 == checksum2

@given(data_strategy, data_strategy, st.integers())
def test_adler32_running_checksum(data1, data2, initial_value):
    checksum1 = zlib.adler32(data1, initial_value)
    checksum2 = zlib.adler32(data2, checksum1)
    combined_checksum = zlib.adler32(data1 + data2, initial_value)
    assert checksum2 == combined_checksum
# End program