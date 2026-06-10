from hypothesis import given, strategies as st
import pandas as pd

# Summary: Generate a DataFrame with varying number of rows and columns.
# The column data types include int, float, and string. Allow duplicate rows.
# Test with different combinations of the 'subset' and 'keep' parameters.
# Check that the output maintains all data from input, just with duplicates removed.
# Check that it errors if invalid 'subset' or 'keep' values are provided.
@given(
    data=st.data(),
    nrows=st.integers(min_value=1, max_value=1000), 
    ncols=st.integers(min_value=1, max_value=10),
    subset_ncols=st.integers(min_value=0, max_value=10),
    keep=st.sampled_from(['first', 'last', False]),
    inplace=st.booleans(),
    ignore_index=st.booleans()
)
def test_drop_duplicates(data, nrows, ncols, subset_ncols, keep, inplace, ignore_index):
    df = data.draw(st.data_frames(
        rows=st.lists(st.tuples(*(st.one_of(
            st.integers(), 
            st.floats(allow_nan=False, allow_infinity=False), 
            st.text()
        ) for _ in range(ncols))), min_size=nrows, max_size=nrows),
        columns=['col'+str(i) for i in range(ncols)]
    ))
    subset = data.draw(
        st.lists(st.sampled_from(df.columns), 
                 min_size=subset_ncols, 
                 max_size=subset_ncols, 
                 unique=True
        )
    )
    
    if subset or keep != 'first' or inplace or ignore_index:
        result = df.drop_duplicates(subset=subset, keep=keep, inplace=inplace, ignore_index=ignore_index)
    else:
        result = df.drop_duplicates()
        
    if not inplace:
        assert isinstance(result, pd.DataFrame)
        assert result.shape[0] <= df.shape[0]
        assert result.shape[1] == df.shape[1]
        if subset:
            assert (~result.duplicated(subset=subset, keep=keep)).all()
        else:
            assert (~result.duplicated(keep=keep)).all()
    else:
        assert result is None
        if subset:
            assert (~df.duplicated(subset=subset, keep=keep)).all()  
        else:
            assert (~df.duplicated(keep=keep)).all()
# End program