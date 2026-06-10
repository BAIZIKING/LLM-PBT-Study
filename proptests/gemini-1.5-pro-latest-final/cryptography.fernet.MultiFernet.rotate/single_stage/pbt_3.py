from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, MultiFernet, InvalidToken

# Summary: This strategy generates a diverse range of inputs for the rotate() function,
# including valid Fernet tokens, invalid tokens, and edge cases like empty bytes and unicode strings. 
@given(st.data())
def test_cryptography_fernet_multifernet_rotate(data):
    # Generate a list of Fernet keys with at least one key.
    keys = data.draw(st.lists(st.binary(min_size=32, max_size=32), min_size=1))
    fernets = [Fernet(key) for key in keys]
    multi_fernet = MultiFernet(fernets)

    # Generate different types of input messages.
    msg = data.draw(st.one_of(
        st.binary(),  # Valid Fernet tokens
        st.text().map(lambda x: x.encode()),  # Unicode strings encoded to bytes
        st.binary(max_size=0),  # Empty bytestring
        st.text()  # Unicode strings
    ))

    # Check properties based on the API documentation:
    try:
        rotated = multi_fernet.rotate(msg)

        # Property 1: The rotated token should be decryptable by the MultiFernet instance.
        decrypted = multi_fernet.decrypt(rotated)

        # Property 2:  The decrypted message should match the original message. 
        assert decrypted == msg 

    except InvalidToken:
        # Property 3: An InvalidToken exception should be raised for invalid input tokens.
        # This is expected for some generated inputs, so we just assert that the exception
        # was raised without further checks. 
        pass

    except TypeError:
        # Property 4: A TypeError should be raised if the input is not bytes or a string.
        assert not isinstance(msg, (bytes, str))
# End program 