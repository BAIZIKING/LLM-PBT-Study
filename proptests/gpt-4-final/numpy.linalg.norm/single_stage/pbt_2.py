import numpy as np
from hypothesis import given, strategies as st
from random import choice

@given(st.data())
def test_linalg_norm(data):
    # Generate a random order
    order_choice = [None, 'fro', 'nuc', float('inf'), float('-inf'), 
                    data.draw(st.integers())]
    order = choice(order_choice)
    
    # Generate random axis
    axis_choice = [None, data.draw(st.integers()), 
                   (data.draw(st.integers()), data.draw(st.integers()))]
    axis = choice(axis_choice)

    # Generate 1-D or 2-D array
    x = data.draw(st.one_of(st.lists(st.integers()), 
                            st.lists(st.lists(st.integers()))))
 
    norm_value = np.linalg.norm(x, ord=order, axis=axis)

    assert isinstance(norm_value, (np.float64, np.ndarray))
    if order == None:
        assert norm_value >= 0
    elif order == float('inf'):
        assert norm_value >= max(np.sum(np.abs(x), axis=1))
    elif order == float('-inf'):
        assert norm_value <= min(np.sum(np.abs(x), axis=1))

    # Test that no exceptions are raised
    try:
        np.linalg.norm(x, ord=order, axis=axis)
    except:
        assert False