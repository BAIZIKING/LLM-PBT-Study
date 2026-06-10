from hypothesis import given, strategies as st

# Summary: Generate valid Fernet tokens by creating MultiFernet instances from
# fresh keys and encrypting random binary plaintext. The token is sometimes
# converted to str to test both accepted input types. A second MultiFernet with
# a new primary key (plus all original keys) is used to rotate the token. We
# verify round-trip correctness, timestamp preservation, and that bytes are returned.
@given(st.data())
def test_cryptography_fernet_MultiFernet_rotate(data):
    from cryptography.fernet import Fernet, MultiFernet

    # Generate random plaintext (covers empty, short, long, arbitrary binary).
    plaintext = data.draw(st.binary(min_size=0, max_size=256))

    # Build an initial MultiFernet with 1..4 fresh keys.
    n_keys = data.draw(st.integers(min_value=1, max_value=4))
    original_keys = [Fernet(Fernet.generate_key()) for _ in range(n_keys)]
    f = MultiFernet(original_keys)

    # Produce a genuine valid token.
    token_bytes = f.encrypt(plaintext)

    # Optionally pass the token as a str to exercise both accepted types.
    as_str = data.draw(st.booleans())
    token = token_bytes.decode("ascii") if as_str else token_bytes

    # Build a rotating MultiFernet with a brand-new primary key + all originals,
    # so decryption still succeeds but re-encryption uses the new key.
    new_primary = Fernet(Fernet.generate_key())
    f2 = MultiFernet([new_primary] + original_keys)

    rotated = f2.rotate(token)

    # Property 1: the return value is bytes.
    assert isinstance(rotated, bytes)

    # Property 2: decrypting the rotated token recovers the original plaintext.
    assert f2.decrypt(rotated) == plaintext

    # Property 4 (sanity): the original-keyed MultiFernet alone (without the new
    # primary key) should NOT be able to decrypt the rotated token, confirming it
    # was re-encrypted under the new primary key.
    from cryptography.fernet import InvalidToken
    try:
        f.decrypt(rotated)
        # If decryption unexpectedly succeeds, the new key must coincide (impossible
        # for freshly generated keys), so this branch should not be reached.
        assert False, "rotated token should not decrypt under original keys only"
    except InvalidToken:
        pass

    # Property 3: timestamp preservation. Extract timestamps and compare.
    ts_original = f.extract_timestamp(token_bytes)
    ts_rotated = f2.extract_timestamp(rotated)
    assert ts_original == ts_rotated
# End program