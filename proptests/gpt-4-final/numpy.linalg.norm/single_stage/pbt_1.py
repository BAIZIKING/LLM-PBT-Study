from hypothesis import given, strategies as st
import numpy as np

@given(st.data())
def test_linalg_norm(data):
    x = data.draw(st.one_of(st.lists(st.floats()), st.lists(st.lists(st.floats())))) # 1D or 2D list of floats
    ord = data.draw(st.one_of(st.floats(min_value=0.0), st.just('fro'), st.just('nuc')))
    axis = data.draw(st.one_of(st.none(), st.integers(), st.tuples(st.integers(), st.integers())))
    keepdims = data.draw(st.booleans())
    
    x_array = np.array(x)
    try:
        result = np.linalg.norm(x_array, ord=ord, axis=axis, keepdims=keepdims)
        if keepdims:
            assert result.ndim == x_array.ndim
            assert any(res == 1 for res in result.shape)
        else:
            assert result.ndim < x_array.ndim
    except ValueError:
        assert ((ord in {'fro', 'nuc'} and x_array.ndim != 2)
                or (isinstance(axis, int) and x_array.ndim not in {1, 2})
                or (isinstance(axis, tuple) and x_array.ndim < 2))