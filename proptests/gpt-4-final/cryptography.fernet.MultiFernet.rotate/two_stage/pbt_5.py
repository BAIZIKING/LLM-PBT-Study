from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, MultiFernet

def test_cryptography_fernet_multifernet_rotate_property():

    @given(st.binary(), st.binary(), st.binary())
    def test_type_consistency_and_message_consistency(key1, key2, msg):
        key1 = Fernet(Fernet.generate_key())
        key2 = Fernet(Fernet.generate_key())
        f = MultiFernet([key1, key2])
        token = f.encrypt(msg)
        rotated = f.rotate(token)
        # Assert type consistency
        assert isinstance(rotated, bytes)
        # Assert message consistency
        decrypted = f.decrypt(rotated)
        assert decrypted == msg

    @given(st.text())
    def test_invalid_token_exception(msg):
        key1 = Fernet(Fernet.generate_key())
        f = MultiFernet([key1])
        try:
            f.rotate(msg)
        except Exception as e:
            assert isinstance(e, cryptography.fernet.InvalidToken)
    
    @given(st.integers())
    def test_type_exception(msg):
        key1 = Fernet(Fernet.generate_key())
        f = MultiFernet([key1])
        try:
            f.rotate(msg)
        except Exception as e:
            assert isinstance(e, TypeError)
    
    @given(st.binary(), st.binary(), st.binary())
    def test_key_rotation_compliance(old_key, new_key, msg):
        old_key = Fernet(Fernet.generate_key())
        f = MultiFernet([old_key])
        token = f.encrypt(msg)

        new_key = Fernet(Fernet.generate_key())
        f2 = MultiFernet([new_key, old_key])
        rotated = f2.rotate(token)
        # Attempt to decrypt with old key should fail
        try:
            old_key.decrypt(rotated)
        except Exception as e:
            assert isinstance(e, cryptography.fernet.InvalidToken)
# End program