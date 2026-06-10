from hypothesis import given, strategies as st
import cryptography.fernet as fernet

# Define strategies for generating keys and messages
keys_strategy = st.lists(st.binary(min_size=32, max_size=32), min_size=2, max_size=5)
message_strategy = st.binary(max_size=1024)  # Limit message size to avoid overflow


@given(keys_strategy, message_strategy)
def test_fernet_multifernet_rotate_output_format(keys, message):
    fernets = [fernet.Fernet(key) for key in keys]
    f = fernet.MultiFernet(fernets)
    token = f.encrypt(message)
    rotated = f.rotate(token)
    assert isinstance(rotated, bytes)  # Check if the output is a byte string
    try:
        fernet.Fernet(b'').decode(rotated)  # Try decoding as base64
    except (binascii.Error, ValueError):
        assert False, "Output is not valid base64-encoded bytes"


@given(keys_strategy, message_strategy)
def test_fernet_multifernet_rotate_decryptable_with_new_key(keys, message):
    fernets = [fernet.Fernet(key) for key in keys]
    f = fernet.MultiFernet(fernets)
    token = f.encrypt(message)

    # Create a new MultiFernet instance with a new key at the front
    new_key = fernet.Fernet.generate_key()
    f2 = fernet.MultiFernet([fernet.Fernet(new_key)] + fernets)
    rotated = f2.rotate(token)

    decrypted = f2.decrypt(rotated)
    assert decrypted == message


@given(keys_strategy, message_strategy)
def test_fernet_multifernet_rotate_not_decryptable_with_old_key(keys, message):
    fernets = [fernet.Fernet(key) for key in keys]
    f = fernet.MultiFernet(fernets)
    token = f.encrypt(message)

    # Rotate the token
    new_key = fernet.Fernet.generate_key()
    f2 = fernet.MultiFernet([fernet.Fernet(new_key)] + fernets)
    rotated = f2.rotate(token)

    # Try decrypting with an old key that is no longer in f2
    old_key = fernets.pop()
    with pytest.raises(fernet.InvalidToken):
        old_key.decrypt(rotated)


@given(keys_strategy, message_strategy)
def test_fernet_multifernet_rotate_preserves_timestamp(keys, message):
    fernets = [fernet.Fernet(key) for key in keys]
    f = fernet.MultiFernet(fernets)
    token = f.encrypt(message)
    rotated = f.rotate(token)

    # Extract timestamps (assuming Fernet token structure)
    original_timestamp = fernet.Fernet(b'').extract_timestamp(token)
    rotated_timestamp = fernet.Fernet(b'').extract_timestamp(rotated)
    assert original_timestamp == rotated_timestamp


@given(keys_strategy, message_strategy)
def test_fernet_multifernet_rotate_different_from_original(keys, message):
    fernets = [fernet.Fernet(key) for key in keys]
    f = fernet.MultiFernet(fernets)
    token = f.encrypt(message)
    rotated = f.rotate(token)
    assert rotated != token
# End program