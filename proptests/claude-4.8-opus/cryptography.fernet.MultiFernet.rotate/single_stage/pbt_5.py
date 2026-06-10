from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, MultiFernet

# Summary: Generate random plaintext payloads and a set of Fernet keys, build a
# MultiFernet to produce a valid token, then a second MultiFernet that prepends a
# fresh primary key (a realistic rotation scenario). Verify rotate() returns bytes,
# preserves the decrypted plaintext, and preserves the original timestamp.
@given(st.data())
def test_cryptography_fernet_MultiFernet_rotate(data):
    # Generate a random plaintext message (including empty and large payloads)
    plaintext = data.draw(st.binary(min_size=0, max_size=1024))

    # Generate between 1 and 5 existing Fernet keys
    num_keys = data.draw(st.integers(min_value=1, max_value=5))
    existing_keys = [Fernet(Fernet.generate_key()) for _ in range(num_keys)]

    # f1 encrypts the original token
    f1 = MultiFernet(existing_keys)
    token = f1.encrypt(plaintext)

    # Optionally pass the token as str (documentation allows bytes or str)
    pass_as_str = data.draw(st.booleans())
    msg = token.decode("utf-8") if pass_as_str else token

    # f2 prepends a new primary key while retaining all old keys (rotation scenario)
    new_primary = Fernet(Fernet.generate_key())
    f2 = MultiFernet([new_primary] + existing_keys)

    rotated = f2.rotate(msg)

    # Property 1: return type is bytes
    assert isinstance(rotated, bytes)

    # Property 2: decrypting the rotated token yields the original plaintext
    assert f2.decrypt(rotated) == plaintext

    # Property 3: timestamp is preserved through rotation
    original_ts = f2.extract_timestamp(token)
    rotated_ts = f2.extract_timestamp(rotated)
    assert original_ts == rotated_ts

    # Property 4: the rotated token is decryptable specifically by the new primary key,
    # confirming re-encryption happened under the primary key
    assert new_primary.decrypt(rotated) == plaintext
# End program