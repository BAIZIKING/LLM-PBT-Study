from hypothesis import given, strategies as st

# Summary: Generate random binary plaintexts and a variable number of Fernet keys.
# Build an initial MultiFernet to produce a valid token, then create a rotated
# MultiFernet that prepends a new primary key while retaining the old keys
# (canonical key-rotation scenario). Verify that rotate() returns bytes, the
# rotated token still decrypts to the original plaintext, and the original
# timestamp is preserved.
@given(st.data())
def test_cryptography_fernet_MultiFernet_rotate(data):
    from cryptography.fernet import Fernet, MultiFernet

    # Generate random plaintext (covers empty, short, long, arbitrary binary).
    message = data.draw(st.binary(min_size=0, max_size=512))

    # Generate a variable number of original keys (1..5).
    num_keys = data.draw(st.integers(min_value=1, max_value=5))
    original_keys = [Fernet(Fernet.generate_key()) for _ in range(num_keys)]

    # Initial MultiFernet and a token encrypted under its primary key.
    f1 = MultiFernet(original_keys)
    token = f1.encrypt(message)

    # New primary key prepended -> rotation-capable MultiFernet that still
    # shares all the old keys, so it can decrypt the original token.
    new_key = Fernet(Fernet.generate_key())
    f2 = MultiFernet([new_key] + original_keys)

    # Capture the original timestamp for preservation check.
    original_ts = f2.extract_timestamp(token)

    # --- Perform rotation ---
    rotated = f2.rotate(token)

    # Property 1: return type is bytes.
    assert isinstance(rotated, bytes)

    # Property 2: round-trip correctness — rotated token decrypts to original.
    assert f2.decrypt(rotated) == message

    # Property 3: timestamp is preserved across rotation.
    assert f2.extract_timestamp(rotated) == original_ts

    # Property 4: rotated token is decryptable using only the new primary key,
    # confirming it was re-encrypted under the primary key.
    f_new_only = MultiFernet([new_key])
    assert f_new_only.decrypt(rotated) == message
# End program