from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(st.data())
def test_pandas_isna_nat(data):
    input_array = data.draw(st.arrays(np.datetime64, shape=st.tuples(st.integers(min_value=1, max_value=10), 
                                                                   st.integers(min_value=1, max_value=10)), 
                                     elements=st.one_of(st.none(), st.datetimes())))
    output_array = pd.isna(input_array)
    for i in range(input_array.shape[0]):
        for j in range(input_array.shape[1]):
            if pd.isna(input_array[i, j]):
                assert output_array[i, j] == True
# End program