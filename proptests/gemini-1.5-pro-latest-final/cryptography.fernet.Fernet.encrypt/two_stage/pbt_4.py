from hypothesis import given, strategies as st
import cryptography.fernet as fernet

@given(message_strategy, st.integers(min_value=0, max_value=len(message)-1))
def test_fernet_tampering(message, index_to_modify):
    key = fernet.Fernet.generate_key()
    f = fernet.Fernet(key)
    encrypted = f.encrypt(message)
    # Modify a byte in the encrypted message
    modified_encrypted = bytearray(encrypted)
    modified_encrypted[index_to_modify] ^= 0xFF
    try:
        f.decrypt(modified_encrypted)
        assert False  # Should raise an exception
    except cryptography.fernet.InvalidToken:
        pass
# End program 