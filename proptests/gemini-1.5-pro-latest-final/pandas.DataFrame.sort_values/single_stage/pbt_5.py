from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# Summary: Generate diverse DataFrames and sort parameters
@given(
    st.data()
)
def test_pandas_dataframe_sort_values(data):
    # Generate DataFrame
    nrows = data.draw(st.integers(min_value=1, max_value=100))
    ncols = data.draw(st.integers(min_value=1, max_value=10))
    df = pd.DataFrame(np.random.randn(nrows, ncols))
    df['str_col'] = pd.Series(data.draw(st.lists(st.text(), min_size=nrows)))
    df['mixed_col'] = pd.Series(data.draw(
        st.lists(st.one_of(st.integers(), st.floats(), st.text()), min_size=nrows)))
    df = df.mask(np.random.random(df.shape) < 0.1)  # Introduce NaN

    # Generate sort parameters
    by = data.draw(
        st.lists(st.sampled_from(df.columns), min_size=1, max_size=3)
    )
    axis = data.draw(st.sampled_from([0, 1]))
    ascending = data.draw(
        st.one_of(
            st.booleans(),
            st.lists(st.booleans(), min_size=len(by), max_size=len(by))
        )
    )
    inplace = data.draw(st.booleans())
    kind = data.draw(st.sampled_from(['quicksort', 'mergesort', 'heapsort']))
    na_position = data.draw(st.sampled_from(['first', 'last']))
    ignore_index = data.draw(st.booleans())

    original_df = df.copy()

    # Sort DataFrame
    result = df.sort_values(
        by=by, axis=axis, ascending=ascending, inplace=inplace, kind=kind,
        na_position=na_position, ignore_index=ignore_index
    )

    # Check properties
    assert result.shape == original_df.shape

    if not inplace:
        assert df.equals(original_df)  # Original unchanged
    else:
        assert result is None  # Inplace sorting returns None

    # Check sorting order based on parameters (implementation omitted for brevity)
    # ...

    if ignore_index:
        assert result.index.equals(pd.RangeIndex(len(df)))
    else:
        assert result.index.equals(original_df.index)
# End program