from hypothesis import given, strategies as st
from cryptography.fernet import Fernet
import base64, time, struct

@given(st.binary())
def test_cryptography_fernet_Fernet_encrypt(data: bytes):
    # Fernet key generation
    key = Fernet.generate_key()
    f = Fernet(key)

    # Getting encrypted data
    token = f.encrypt(data)

    # Checking that the function does not fail with bytes (throws no exception)
    try:
        f.encrypt(data)
    except TypeError:
        raise Exception("Function is not working properly with bytes")

    # Checking that the return value from encrypt function is a bytes object
    assert isinstance(token, bytes), "Return value is not a bytes object"

    # Encoded time in the message is earlier than or equal to the current time
    timestamp_from_msg = int.from_bytes(token[1:9], "big")
    assert timestamp_from_msg <= int(time.time()), "Encoded time in the message is not earlier than or equal to the current time"
    
# End program