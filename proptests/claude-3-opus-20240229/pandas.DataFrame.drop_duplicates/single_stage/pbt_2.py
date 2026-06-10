from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# Summary: Generate a DataFrame with random number of rows, columns, column names, 
# and cell values. Test subset, keep, and ignore_index parameters with 
# various strategies. Check the expected number of rows after dropping duplicates 
# and properties of the returned DataFrame.
@given(
    data=st.data(),
    nrows=st.integers(min_value=1, max_value=100),
    ncols=st.integers(min_value=1, max_value=10),
    subset_strategy=st.sampled_from([
        st.none(), 
        st.lists(st.integers(min_value=0, max_value=9), min_size=1, max_size=5, unique=True)
    ]),
    keep_strategy=st.sampled_from(['first', 'last', False]),
    ignore_index=st.booleans(),
    inplace=st.booleans()
)
def test_drop_duplicates(data, nrows, ncols, subset_strategy, keep_strategy, ignore_index, inplace):
    # Generate random column names
    colnames = data.draw(st.lists(st.text(min_size=1, max_size=10), min_size=ncols, max_size=ncols, unique=True))

    # Generate random cell values
    cell_values = data.draw(st.lists(
        st.one_of(
            st.integers(),
            st.floats(allow_nan=False, allow_infinity=False),
            st.text()
        ),
        min_size=nrows*ncols, max_size=nrows*ncols
    ))

    # Create DataFrame with random values  
    df = pd.DataFrame(np.reshape(cell_values, (nrows, ncols)), columns=colnames)

    # Generate subset parameter
    subset = data.draw(subset_strategy)
    if isinstance(subset, list):
        subset = [colnames[i] for i in subset]

    # Call drop_duplicates
    result = df.drop_duplicates(subset=subset, keep=keep_strategy, ignore_index=ignore_index, inplace=inplace)

    if inplace:
        assert result is None
        result = df
    else:
        assert isinstance(result, pd.DataFrame)
        
    # Check number of rows
    if subset is None:
        subset = colnames
    if keep_strategy == False:
        expected_nrows = len(df[subset].drop_duplicates(keep=False)) 
    else:
        expected_nrows = len(df[subset].drop_duplicates(keep=keep_strategy))
    assert len(result) == expected_nrows

    if ignore_index:
        assert list(result.index) == list(range(len(result)))
    else:
        assert result.index.equals(df.index)
# End program