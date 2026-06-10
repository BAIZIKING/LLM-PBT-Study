from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(st.data())
def test_pandas_isna(data):
    # Generate scalar
    scalar = data.draw(st.one_of(st.integers(), st.floats(allow_nan=True), st.none(), st.text()))
    assert isinstance(pd.isna(scalar), bool)
    
    # Generate array-like objects
    array_obj = data.draw(st.one_of(st.lists(st.floats(allow_nan=True)), st.dictionaries(st.text(), st.floats(allow_nan=True))))
    assert isinstance(pd.isna(array_obj), type(array_obj)) 
    
    # Generate numpy array
    np_array = data.draw(st.lists(st.floats(allow_nan=True)).map(np.array))
    assert isinstance(pd.isna(np_array), np.ndarray)
    
    # Check the returned values correctly indicate whether the input values are null or NaN
    if scalar is None or (isinstance(scalar, float) and np.isnan(scalar)):
        assert pd.isna(scalar) == True
    else:
        assert pd.isna(scalar) == False
        
    for elem in array_obj:
        if elem is None or (isinstance(elem, float) and np.isnan(elem)):
            assert pd.isna(array_obj)[elem] == True
        else:
            assert pd.isna(array_obj)[elem] == False
    
    for elem in np.nditer(np_array):
        if np.isnan(elem):
            assert pd.isna(elem.item()) == True 
        else:
            assert pd.isna(elem.item()) == False