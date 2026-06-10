from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(st.data())
def test_pandas_isna_all_missing(data):
    input_array = data.draw(st.arrays(dtype=float, elements=st.floats(allow_infinity=False, allow_nan=True), shape=st.tuples(st.integers(min_value=1, max_value=100), st.integers(min_value=1, max_value=100))))
    input_array[:] = np.nan
    output_array = pd.isna(input_array)
    assert np.all(output_array == True)
# End program