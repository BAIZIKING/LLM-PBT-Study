from hypothesis import given, strategies as st
import pandas as pd

# Summary: Generates diverse DataFrames and parameters for drop_duplicates
@given(st.data())
def test_pandas_dataframe_drop_duplicates(data):
    # Generate DataFrame
    df = data.draw(st.data_frames(
        columns=st.lists(st.column_names(), min_size=1),
        rows=st.lists(st.one_of(
            st.integers(), st.floats(allow_nan=False), st.text(), 
            st.datetimes(), st.booleans()
        ), min_size=1)
    ))
    
    # Generate parameters
    subset = data.draw(st.one_of(st.none(), st.lists(st.column_names())))
    keep = data.draw(st.sampled_from(["first", "last", False]))
    inplace = data.draw(st.booleans())
    ignore_index = data.draw(st.booleans())
    
    # Apply drop_duplicates and store original DataFrame for comparison
    original_df = df.copy()
    result_df = df.drop_duplicates(subset=subset, keep=keep, inplace=inplace, ignore_index=ignore_index)
    
    # Check returned DataFrame shape
    if not inplace:
        assert df.shape == original_df.shape  # Original DataFrame unchanged
    if subset is None:
        expected_columns = original_df.columns
    else:
        expected_columns = subset
    assert all(col in result_df.columns for col in expected_columns)
    
    # Check duplicate removal
    if keep == "first":
        assert result_df.shape[0] <= original_df.shape[0]
        assert not any(result_df[subset].duplicated(keep=False))
    elif keep == "last":
        assert result_df.shape[0] <= original_df.shape[0]
        assert not any(result_df[subset].duplicated(keep="last"))
    elif keep is False:
        assert result_df.shape[0] == result_df[subset].drop_duplicates().shape[0]
        
    # Check index behavior
    if ignore_index:
        assert result_df.index.equals(pd.RangeIndex(start=0, stop=len(result_df)))
    else:
        if not inplace:
            assert result_df.index.equals(original_df.index)
        
# End program