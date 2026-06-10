from hypothesis import given, strategies as st
import cryptography.fernet as fernet

# Define a strategy for generating Fernet keys
keys_strategy = st.lists(st.binary(min_size=32, max_size=32), min_size=2, max_size=5)

# Define a strategy for generating tokens (bytes or strings)
tokens_strategy = st.one_of(st.binary(), st.text())

@given(keys_strategy, tokens_strategy)
def test_rotate_output_type(keys, token):
    f = fernet.MultiFernet([fernet.Fernet(key) for key in keys])
    rotated = f.rotate(token)
    assert isinstance(rotated, bytes)

@given(keys_strategy, tokens_strategy)
def test_rotate_output_length(keys, token):
    f = fernet.MultiFernet([fernet.Fernet(key) for key in keys])
    rotated = f.rotate(token)
    # Length should be consistent for a given set of keys and independent of token content
    assert len(rotated) == len(f.rotate(b"test")) 

@given(keys_strategy, tokens_strategy)
def test_rotate_decryptable_new_key(keys, token):
    f1 = fernet.MultiFernet([fernet.Fernet(key) for key in keys])
    f2 = fernet.MultiFernet([fernet.Fernet(fernet.Fernet.generate_key())] + keys)
    rotated = f2.rotate(token)
    # Rotated token should be decryptable with the new primary key in f2
    assert f2.decrypt(rotated) == token 

@given(keys_strategy, tokens_strategy)
def test_rotate_not_decryptable_old_key(keys, token):
    f1 = fernet.MultiFernet([fernet.Fernet(key) for key in keys])
    f2 = fernet.MultiFernet([fernet.Fernet(fernet.Fernet.generate_key())] + keys)
    rotated = f2.rotate(token)
    # Rotated token should NOT be decryptable with the old primary key from f1
    with pytest.raises(fernet.InvalidToken):
        f1.decrypt(rotated) 

@given(keys_strategy, tokens_strategy)
def test_rotate_timestamp_preserved(keys, token):
    f1 = fernet.MultiFernet([fernet.Fernet(key) for key in keys])
    f2 = fernet.MultiFernet([fernet.Fernet(fernet.Fernet.generate_key())] + keys)
    token = f1.encrypt(b"test")
    rotated = f2.rotate(token)
    # Extract timestamps from original and rotated tokens
    original_timestamp = fernet.Fernet._get_unverified_token_data(token)[1]
    rotated_timestamp = fernet.Fernet._get_unverified_token_data(rotated)[1]
    assert original_timestamp == rotated_timestamp

# End program