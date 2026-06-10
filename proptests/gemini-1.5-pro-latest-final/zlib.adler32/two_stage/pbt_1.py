from hypothesis import given, strategies as st
import zlib

# Define a strategy for generating data, limiting size to avoid potential overflows
data_strategy = st.binary(max_size=1024)

@given(data_strategy)
def test_empty_input(data):
    assert zlib.adler32(b"") == 1

@given(st.binary(min_size=1, max_size=1))
def test_single_byte_determinism(data):
    first_checksum = zlib.adler32(data)
    second_checksum = zlib.adler32(data)
    assert first_checksum == second_checksum

@given(data_strategy, data_strategy)
def test_order_independence(data1, data2):
    combined_data_1 = data1 + data2
    combined_data_2 = data2 + data1
    assert zlib.adler32(combined_data_1) == zlib.adler32(combined_data_2)

@given(data_strategy, data_strategy, data_strategy)
def test_running_checksum(data1, data2, data3):
    checksum_a = zlib.adler32(data1)
    checksum_b = zlib.adler32(data2, checksum_a)
    checksum_c = zlib.adler32(data3, checksum_b)
    combined_checksum = zlib.adler32(data1 + data2 + data3)
    assert checksum_c == combined_checksum

@given(data_strategy)
def test_data_alteration(data):
    original_checksum = zlib.adler32(data)
    modified_data = bytearray(data)
    # Modify a random byte (if data is not empty)
    if modified_data:
        index_to_modify = st.integers(min_value=0, max_value=len(data) - 1).example()
        modified_data[index_to_modify] ^= 0xFF  # Flip a bit to ensure modification
    modified_checksum = zlib.adler32(modified_data)
    assert original_checksum != modified_checksum
# End program