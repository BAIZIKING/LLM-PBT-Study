from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# Define strategies for input data
array_strategy = st.arrays(np.float64, min_size=1, max_size=100, elements=st.floats(allow_nan=True))
bins_strategy = st.one_of(
    st.integers(min_value=2, max_value=10),  # Number of bins
    st.lists(st.floats(allow_infinity=False), min_size=2, unique=True),  # Custom bin edges
)
labels_strategy = st.one_of(st.none(), st.booleans(), st.lists(st.text()))

@given(data=st.data())
def test_pandas_cut_output_dtype(data):
    x = data.draw(array_strategy)
    bins = data.draw(bins_strategy)
    labels = data.draw(labels_strategy)
    
    result = pd.cut(x, bins, labels=labels)
    
    if labels is False:
        assert result.dtype == np.dtype('int64')
    else:
        assert pd.api.types.is_categorical_dtype(result)

@given(data=st.data())
def test_pandas_cut_number_of_elements(data):
    x = data.draw(array_strategy)
    bins = data.draw(bins_strategy)
    
    result = pd.cut(x, bins)
    
    assert len(result) == len(x)

@given(data=st.data())
def test_pandas_cut_nan_values(data):
    x = data.draw(array_strategy)
    bins = data.draw(bins_strategy)
    
    result = pd.cut(x, bins)
    
    assert np.isnan(result).sum() == np.isnan(x).sum() 

@given(data=st.data())
def test_pandas_cut_order_preservation(data):
    x = data.draw(array_strategy)
    bins = data.draw(bins_strategy)
    
    result = pd.cut(x, bins)
    
    assert all(result.argsort() == np.argsort(x))

@given(data=st.data())
def test_pandas_cut_bin_membership(data):
    x = data.draw(array_strategy)
    bins = data.draw(bins_strategy)
    
    result = pd.cut(x, bins, retbins=True)
    categories, bin_edges = result
    
    for value, category in zip(x, categories):
        if pd.isna(value):
            assert pd.isna(category)
        else:
            assert category.left < value <= category.right

# End program