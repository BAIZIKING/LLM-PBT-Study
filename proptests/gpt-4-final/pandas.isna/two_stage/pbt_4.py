from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# A strategy for generating array-like objects of varying size containing numbers, string or None
arraylike = st.one_of(
    st.lists(st.floats(allow_nan=True, allow_infinity=False)),
    st.lists(st.text() | st.none())
)

@given(arraylike)
def test_output_type_and_dimension_match_input(input):
    output = pd.isna(input)
    assert isinstance(output, (bool, np.ndarray))
    assert np.array(input).shape == output.shape

@given(arraylike)
def test_nan_and_none_detection(input):
    output = pd.isna(input)
    for i, value in enumerate(input):
        assert output[i] == (value is None or np.isnan(value))

@given(arraylike)
def test_input_unchanged_by_function(input):
    original_input = input.copy()
    pd.isna(input)
    assert input == original_input

@given(st.lists(arraylike))
def test_isna_on_individual_elements_of_dataframe(input):
    df = pd.DataFrame(input)
    assert pd.isna(df).values.all() == all(pd.isna(x) for row in input for x in row)