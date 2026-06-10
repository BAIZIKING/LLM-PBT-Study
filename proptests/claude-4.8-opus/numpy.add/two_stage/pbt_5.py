from hypothesis import given, strategies as st, assume
import hypothesis.extra.numpy as npst
import numpy


# Strategy for "safe" floats that avoid NaN/inf and very large magnitudes
# that could overflow during addition.
safe_floats = st.floats(
    min_value=-1e150,
    max_value=1e150,
    allow_nan=False,
    allow_infinity=False,
    width=64,
)

# Strategy for safe array shapes (small to keep tests fast).
safe_shapes = npst.array_shapes(min_dims=0, max_dims=3, min_side=0, max_side=4)


def safe_float_arrays(shape):
    return npst.arrays(dtype=numpy.float64, shape=shape, elements=safe_floats)


# A strategy producing two broadcastable float arrays.
broadcastable_pair = npst.mutually_broadcastable_shapes(num_shapes=2).flatmap(
    lambda bs: st.tuples(
        safe_float_arrays(bs.input_shapes[0]),
        safe_float_arrays(bs.input_shapes[1]),
        st.just(bs.result_shape),
    )
)

# A strategy producing three broadcastable float arrays.
broadcastable_triple = npst.mutually_broadcastable_shapes(num_shapes=3).flatmap(
    lambda bs: st.tuples(
        safe_float_arrays(bs.input_shapes[0]),
        safe_float_arrays(bs.input_shapes[1]),
        safe_float_arrays(bs.input_shapes[2]),
        st.just(bs.result_shape),
    )
)


@given(st.data())
def test_numpy_add_commutativity():
    """Property 1: np.add(x1, x2) == np.add(x2, x1) element-wise."""
    @given(broadcastable_pair)
    def inner(pair):
        x1, x2, _ = pair
        result1 = numpy.add(x1, x2)
        result2 = numpy.add(x2, x1)
        assert numpy.array_equal(result1, result2, equal_nan=True)
    inner()
# End program


@given(st.data())
def test_numpy_add_identity_element():
    """Property 2: np.add(x, 0) == x element-wise."""
    @given(safe_shapes.flatmap(lambda s: safe_float_arrays(s)))
    def inner(x):
        result = numpy.add(x, 0)
        assert numpy.array_equal(result, x, equal_nan=True)
    inner()
# End program


@given(st.data())
def test_numpy_add_equivalence_to_operator():
    """Property 3: np.add(x1, x2) == x1 + x2 element-wise."""
    @given(broadcastable_pair)
    def inner(pair):
        x1, x2, _ = pair
        result_func = numpy.add(x1, x2)
        result_op = x1 + x2
        assert numpy.array_equal(result_func, result_op, equal_nan=True)
    inner()
# End program


@given(st.data())
def test_numpy_add_output_shape():
    """Property 4: result shape equals broadcasted shape of inputs."""
    @given(broadcastable_pair)
    def inner(pair):
        x1, x2, result_shape = pair
        result = numpy.add(x1, x2)
        assert result.shape == tuple(result_shape)
    inner()
# End program


@given(st.data())
def test_numpy_add_associativity():
    """Property 5: (x1 + x2) + x3 approx== x1 + (x2 + x3) element-wise."""
    @given(broadcastable_triple)
    def inner(triple):
        x1, x2, x3, _ = triple
        left = numpy.add(numpy.add(x1, x2), x3)
        right = numpy.add(x1, numpy.add(x2, x3))
        # Floating point addition is not exactly associative, so allow
        # for a relative/absolute tolerance.
        assert numpy.allclose(left, right, rtol=1e-9, atol=1e-12, equal_nan=True)
    inner()
# End program