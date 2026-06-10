from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(st.recursive(st.booleans() | st.floats() | st.none() | st.datetimes(), 
                    lambda children: st.lists(children, max_size=5) | st.tuples(children, max_size=5)))
def test_output_type_and_shape(obj):
    result = pd.isna(obj)
    if isinstance(obj, (list, tuple, np.ndarray, pd.Series, pd.DataFrame)):
        assert result.shape == np.array(obj).shape
        assert isinstance(result, np.ndarray)
        assert result.dtype == bool
    else:
        assert isinstance(result, bool)

@given(st.recursive(st.booleans() | st.integers() | st.text(), 
                    lambda children: st.lists(children, max_size=5) | st.tuples(children, max_size=5)))
def test_output_all_false_for_non_missing_values(obj):
    result = pd.isna(obj)
    if isinstance(obj, (list, tuple, np.ndarray, pd.Series, pd.DataFrame)):
        assert (~result).all()
    else:
        assert not result
        
@given(st.sampled_from([np.nan, None, pd.NaT]))
def test_true_for_missing_values(missing_value):
    assert pd.isna(missing_value)
    
@given(st.recursive(st.booleans() | st.floats() | st.none() | st.datetimes(), 
                    lambda children: st.lists(children, max_size=5) | st.tuples(children, max_size=5)))
def test_inverse_of_notna(obj):
    isna_result = pd.isna(obj)
    notna_result = pd.notna(obj)
    if isinstance(obj, (list, tuple, np.ndarray, pd.Series, pd.DataFrame)):
        assert (isna_result == ~notna_result).all()
    else:
        assert isna_result == (not notna_result)
        
# End program