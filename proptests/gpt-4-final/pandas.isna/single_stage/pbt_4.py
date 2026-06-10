from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(st.data())
def test_pandas_isna(data):
    # Drawing from a strategy that generates either scalars (None, np.nan, numeric, non-numeric), or array-like inputs (list or np.array)
    input_obj = data.draw(
        st.one_of(
            st.none(), 
            st.floats(allow_nan=True),
            st.text(), 
            st.lists(
                st.one_of(st.none(), st.floats(allow_nan=True), st.text()), 
                min_size=0, max_size=5), 
            st.just(np.array(
                    data.draw(
                        st.lists(
                            st.one_of(st.none(), st.floats(allow_nan=True), st.text()), 
                            min_size=0, max_size=5
                        )
                    )
                )
            )
        )
    )

    # Call pandas.isna() with the randomly generated input
    result = pd.isna(input_obj)

    # Assert the properties
    if isinstance(input_obj, (list, np.ndarray)):
        assert isinstance(result, (list, np.ndarray))  # The result should be an array-like of booleans
        assert all(isinstance(i, bool) for i in result)  # Each element in the result should be a boolean
        assert all(result[i] == (input_obj[i] is None or pd.isna(input_obj[i])) for i in range(len(result)))  # Correctly identify missing values
    else:
        assert isinstance(result, bool)  # The result should be a boolean
        assert result == (input_obj is None or pd.isna(input_obj))  # Correctly identify missing values
# End program