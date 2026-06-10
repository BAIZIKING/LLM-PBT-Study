from hypothesis import given, strategies as st, settings, assume
import hypothesis.extra.numpy as hnp
import numpy


# ---- Shared array-generation helpers (bounded to avoid overflow/inf) ----

def draw_int_array(data):
    dtype = data.draw(st.sampled_from([numpy.int32, numpy.int64]), label="int_dtype")
    shape = data.draw(
        hnp.array_shapes(min_dims=1, max_dims=3, min_side=1, max_side=6),
        label="int_shape",
    )
    # max size 6^3 = 216 elements, values in [-1000, 1000] -> max |cumsum| ~ 2.16e5,
    # far below int32 limits, so no overflow.
    elements = st.integers(min_value=-1000, max_value=1000)
    return data.draw(hnp.arrays(dtype=dtype, shape=shape, elements=elements),
                     label="int_array")


def draw_float_array(data):
    dtype = data.draw(st.sampled_from([numpy.float32, numpy.float64]),
                      label="float_dtype")
    shape = data.draw(
        hnp.array_shapes(min_dims=1, max_dims=3, min_side=1, max_side=6),
        label="float_shape",
    )
    elements = st.floats(
        min_value=-1e3, max_value=1e3,
        allow_nan=False, allow_infinity=False,
        width=32 if dtype == numpy.float32 else 64,
    )
    return data.draw(hnp.arrays(dtype=dtype, shape=shape, elements=elements),
                     label="float_array")


def draw_axis(data, arr, label):
    return data.draw(st.one_of(st.none(),
                               st.integers(min_value=0, max_value=arr.ndim - 1)),
                     label=label)


@given(st.data())
@settings(max_examples=300)
def test_numpy_cumsum_property(data):
    # ===== Property 1: Output size preservation =====
    arr1 = draw_int_array(data)
    axis1 = draw_axis(data, arr1, "axis1")
    out1 = numpy.cumsum(arr1, axis=axis1)
    assert out1.size == arr1.size
    if axis1 is not None:
        assert out1.shape == arr1.shape

    # ===== Property 2: Last element of flattened cumsum equals sum (integers) =====
    arr2 = draw_int_array(data)
    flat_cumsum = numpy.cumsum(arr2)  # axis=None -> flattened
    assert flat_cumsum[-1] == numpy.sum(arr2)

    # ===== Property 3: First element equals first input element (flattened) =====
    arr3 = draw_int_array(data)
    flat_cumsum3 = numpy.cumsum(arr3)
    assert flat_cumsum3[0] == arr3.ravel()[0]

    # ===== Property 4: diff recovers the input along the cumulative axis =====
    arr4 = draw_int_array(data)
    axis4 = draw_axis(data, arr4, "axis4")
    cs4 = numpy.cumsum(arr4, axis=axis4)
    if axis4 is None:
        # operate on flattened versions
        flat = arr4.ravel()
        reconstructed = numpy.diff(cs4, prepend=0)
        assert numpy.array_equal(reconstructed, flat)
    else:
        reconstructed = numpy.diff(cs4, axis=axis4, prepend=0)
        # prepend=0 inserts a zero slice at the start along axis4 before diffing
        # Build a zero-prepended cumsum manually to compare consistently:
        zero_shape = list(cs4.shape)
        zero_shape[axis4] = 1
        zeros = numpy.zeros(zero_shape, dtype=cs4.dtype)
        padded = numpy.concatenate([zeros, cs4], axis=axis4)
        reconstructed = numpy.diff(padded, axis=axis4)
        assert numpy.array_equal(reconstructed, arr4)

    # ===== Property 5: Output dtype matches specification =====
    # 5a: explicit dtype provided
    arr5 = draw_float_array(data)
    requested_dtype = data.draw(
        st.sampled_from([numpy.float32, numpy.float64]), label="requested_dtype"
    )
    out5 = numpy.cumsum(arr5, dtype=requested_dtype)
    assert out5.dtype == numpy.dtype(requested_dtype)

    # 5b: no dtype -> at least the input dtype for non-low-precision types.
    arr5b = draw_int_array(data)  # int32 or int64
    out5b = numpy.cumsum(arr5b)
    default_int = numpy.dtype(numpy.intp)  # platform default integer
    # numpy promotes integer dtypes of lower precision than default to default.
    if arr5b.dtype.itemsize >= default_int.itemsize:
        assert out5b.dtype == arr5b.dtype
    else:
        assert out5b.dtype == default_int
# End program