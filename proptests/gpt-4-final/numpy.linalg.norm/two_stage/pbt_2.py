from hypothesis import given, strategies as st
from hypothesis.extra import numpy as hn
import numpy as np
import numpy.linalg as LA

# Checking norm value range
@given(hn.arrays(dtype=np.float32, shape=st.integers(min_value=1, max_value=100)))
def test_norm_value(arr):
  norm = LA.norm(arr)
  assert norm >= 0

# Checking consistency with vector norms
@given(hn.arrays(dtype=np.float32, shape=st.tuples(st.integers(1, 10), st.integers(1, 10))))
def test_consistency_with_vector_norms(arr):
  norm1 = LA.norm(arr)
  norm2 = LA.norm(arr.ravel())
  np.testing.assert_almost_equal(norm1, norm2)

# Checking dimension preservation
@given(hn.arrays(dtype=np.float32, shape=st.tuples(st.integers(1, 10), st.integers(1, 10))))
def test_dimension_preservation(arr):
  norm_keepdims = LA.norm(arr, keepdims=True)
  assert arr.ndim == norm_keepdims.ndim

# Checking Axis-based Norming
@given(hn.arrays(dtype=np.float32, shape=st.tuples(st.integers(1, 10), st.integers(1, 10))))
def test_axis_based_norming(arr):
  for axis in range(arr.ndim):
    norm = LA.norm(arr, axis=axis)
    assert len(norm) == arr.shape[axis]

# Checking Ord Parameter Effect
@given(hn.arrays(dtype=np.float32, shape=st.tuples(st.integers(1, 10), st.integers(1, 10))),
       st.sampled_from([None, 'fro', 'nuc', np.inf, -np.inf, 1, -1, 2, -2]))
def test_ord_parameter_effect(arr, ord):
  if ord in ['fro', 'nuc'] and arr.ndim != 2:
    try:
      LA.norm(arr, ord=ord)
    except ValueError:
      assert True
  else:
    assert LA.norm(arr, ord=ord) >= 0