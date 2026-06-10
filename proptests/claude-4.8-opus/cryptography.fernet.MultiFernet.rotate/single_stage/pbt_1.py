from hypothesis import given, strategies as st

# Summary: Generate a random binary payload, encrypt it with a base Fernet key to
# create a valid token (passed as bytes or str), then build a MultiFernet with a
# new primary key plus the original key. Verify that rotation preserves the
# decrypted plaintext, preserves the timestamp, and returns bytes.
@given(st.data())
def test_cryptography_fernet_MultiFernet_rotate(data):
    from cryptography.fernet import Fernet, MultiFernet

    # Generate a random plaintext payload (edge cases: empty, large, arbitrary bytes)
    payload = data.draw(st.binary(min_size=0, max_size=1024))

    # Generate distinct Fernet keys for rotation
    key_old = Fernet(Fernet.generate_key())
    key_new = Fernet(Fernet.generate_key())

    # Create an original valid token using the old key
    f_old = MultiFernet([key_old])
    token = f_old.encrypt(payload)

    # Optionally pass the token as str instead of bytes
    as_str = data.draw(st.booleans())
    msg = token.decode("utf-8") if as_str else token

    # Build a MultiFernet with the new key at the front (rotation scenario)
    f_new = MultiFernet([key_new, key_old])

    rotated = f_new.rotate(msg)

    # Property 1: the return value must be bytes
    assert isinstance(rotated, bytes)

    # Property 2: decrypting the rotated token yields the original payload
    assert f_new.decrypt(rotated) == payload

    # Property 3: the rotated token is encrypted under the new primary key,
    # so a MultiFernet with only the new key must decrypt it.
    f_only_new = MultiFernet([key_new])
    assert f_only_new.decrypt(rotated) == payload

    # Property 4: the timestamp is preserved across rotation
    ts_original = f_old.extract_timestamp(token)
    ts_rotated = f_new.extract_timestamp(rotated)
    assert ts_original == ts_rotated
# End program