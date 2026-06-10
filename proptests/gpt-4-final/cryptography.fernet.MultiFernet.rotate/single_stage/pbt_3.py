from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, MultiFernet

@given(st.text(min_size=0))
def test_multiFernet_rotate(msg):
    fernet_instance = MultiFernet([Fernet(Fernet.generate_key()), Fernet(Fernet.generate_key())])
    encrypted_msg = fernet_instance.encrypt(msg.encode())
    rotated_msg = fernet_instance.rotate(encrypted_msg)
    assert isinstance(rotated_msg, bytes)
    decrypted_msg = fernet_instance.decrypt(rotated_msg)
    assert decrypted_msg.decode() == msg
# End program