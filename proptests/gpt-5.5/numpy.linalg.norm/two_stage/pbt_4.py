from hypothesis import given, strategies as st
import numpy

_FLOATS = st.floats(
    min_value=-100.0,
    max_value=100.0,
    allow_nan=False,
    allow_infinity=False,
    width=32,
)


def _shape_strategy(min_ndim=1, max_ndim=3, max_side=4):
    return st.lists(
        st.integers(min_value=1, max_value=max_side),
        min_size=min_ndim,
        max_size=max_ndim,
    ).map(tuple)


def _array_from_shape(data, shape, elements=_FLOATS):
    size = int(numpy.prod(shape))
    values = data.draw(st.lists(elements, min_size=size, max_size=size))
    return numpy.array(values, dtype=float).reshape(shape)


def _valid_axis_none_ord(data, ndim):
    if ndim == 1:
        return data.draw(
            st.sampled_from(
                [None, numpy.inf, -numpy.inf, 0, 1, -1, 2, -2, 3, -3]
            )
        )
    if ndim == 2:
        return data.draw(
            st.sampled_from(
                [None, "fro", "nuc", numpy.inf, -numpy.inf, 1, -1, 2, -2]
            )
        )
    return None


@given(st.data())
def test_numpy_linalg_norm_property_non_negative(data):
    shape = data.draw(_shape_strategy(max_ndim=3, max_side=4))
    x = _array_from_shape(data, shape)
    ord_value = _valid_axis_none_ord(data, len(shape))

    with numpy.errstate(all="ignore"):
        result = numpy.linalg.norm(x, ord=ord_value)

    result_array = numpy.asarray(result)
    assert numpy.all(numpy.isfinite(result_array))
    assert numpy.all(result_array >= -1e-7)


@given(st.data())
def test_numpy_linalg_norm_property_zero_input_has_zero_norm(data):
    shape = data.draw(_shape_strategy(max_ndim=3, max_side=4))
    x = numpy.zeros(shape, dtype=float)
    ord_value = _valid_axis_none_ord(data, len(shape))

    with numpy.errstate(all="ignore"):
        result = numpy.linalg.norm(x, ord=ord_value)

    assert numpy.allclose(result, 0.0, rtol=0.0, atol=1e-10)


@given(st.data())
def test_numpy_linalg_norm_property_scalar_homogeneity(data):
    ndim = data.draw(st.integers(min_value=1, max_value=2))
    shape = data.draw(_shape_strategy(min_ndim=ndim, max_ndim=ndim, max_side=4))
    x = _array_from_shape(data, shape)
    scalar = data.draw(_FLOATS)

    if ndim == 1:
        ord_value = data.draw(st.sampled_from([None, numpy.inf, -numpy.inf, 1, 2, 3]))
    else:
        ord_value = data.draw(
            st.sampled_from(
                [None, "fro", "nuc", numpy.inf, -numpy.inf, 1, -1, 2, -2]
            )
        )

    with numpy.errstate(all="ignore"):
        scaled_norm = numpy.linalg.norm(scalar * x, ord=ord_value)
        expected = abs(scalar) * numpy.linalg.norm(x, ord=ord_value)

    assert numpy.allclose(scaled_norm, expected, rtol=1e-6, atol=1e-6)


@given(st.data())
def test_numpy_linalg_norm_property_default_is_flattened_euclidean_norm(data):
    shape = data.draw(_shape_strategy(max_ndim=3, max_side=4))
    x = _array_from_shape(data, shape)

    result = numpy.linalg.norm(x)
    expected = numpy.sqrt(numpy.sum(numpy.abs(x.ravel()) ** 2))

    assert numpy.allclose(result, expected, rtol=1e-12, atol=1e-12)


@given(st.data())
def test_numpy_linalg_norm_property_axis_and_keepdims_shape(data):
    shape = data.draw(_shape_strategy(max_ndim=4, max_side=3))
    ndim = len(shape)
    x = _array_from_shape(data, shape)
    keepdims = data.draw(st.booleans())

    use_matrix_axis = ndim >= 2 and data.draw(st.booleans())

    if use_matrix_axis:
        axes = tuple(data.draw(st.lists(
            st.integers(min_value=0, max_value=ndim - 1),
            min_size=2,
            max_size=2,
            unique=True,
        )))
        axis = axes
    else:
        axis = data.draw(st.integers(min_value=-ndim, max_value=ndim - 1))
        axes = (axis % ndim,)

    result = numpy.linalg.norm(x, axis=axis, keepdims=keepdims)

    normalized_axes = tuple(a % ndim for a in axes)
    if keepdims:
        expected_shape = tuple(
            1 if i in normalized_axes else shape[i] for i in range(ndim)
        )
    else:
        expected_shape = tuple(
            shape[i] for i in range(ndim) if i not in normalized_axes
        )

    assert numpy.shape(result) == expected_shape
# End program