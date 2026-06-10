from hypothesis import given, strategies as st

# Summary: Generate genuine Fernet tokens by encrypting random binary payloads with a
# MultiFernet built from a random number of keys, then rotate using a second MultiFernet
# that prepends a fresh primary key. Verify round-trip decryption, re-encryption under the
# new primary key, timestamp preservation, and bytes output type.
@given(st.data())
def test_cryptography_fernet_MultiFernet_rotate(data):
    from cryptography.fernet import Fernet, MultiFernet

    # Generate a random payload, including edge cases (empty / large binary).
    payload = data.draw(st.binary(min_size=0, max_size=512))

    # Build the original MultiFernet from 1..4 random keys.
    num_keys = data.draw(st.integers(min_value=1, max_value=4))
    original_keys = [Fernet(Fernet.generate_key()) for _ in range(num_keys)]
    f_original = MultiFernet(original_keys)

    # Encrypt to produce a genuine, valid token.
    token = f_original.encrypt(payload)

    # Create a new primary key and build the rotating MultiFernet by prepending it.
    new_primary_key = Fernet.generate_key()
    new_primary = Fernet(new_primary_key)
    f_rotate = MultiFernet([new_primary] + original_keys)

    # Perform the rotation.
    rotated = f_rotate.rotate(token)

    # Property 1: Output must be bytes.
    assert isinstance(rotated, bytes)

    # Property 2: Round-trip correctness via the rotating MultiFernet.
    assert f_rotate.decrypt(rotated) == payload

    # Property 3: Re-encryption under the new primary key (a Fernet with only that key
    # must be able to decrypt the rotated token).
    primary_only = Fernet(new_primary_key)
    assert primary_only.decrypt(rotated) == payload

    # Property 4: Timestamp preservation. The timestamp extracted from the original token
    # must equal that of the rotated token.
    orig_ts = f_original.extract_timestamp(token)
    rotated_ts = f_rotate.extract_timestamp(rotated)
    assert orig_ts == rotated_ts
# End program