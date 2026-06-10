from hypothesis import given, strategies as st
import pandas as pd

# Summary: 
# Generate a variety of DataFrames and Series to test merging on:
# - Use different data types like ints, floats, strings, bools
# - Vary number of rows (0 to 100) and columns (1 to 10)  
# - Include missing values 
# - Generate both regular and MultiIndex indexes
# - Use different merge parameters:
#   - how: inner, left, right, outer, cross
#   - on, left_on, right_on: column names, index levels, or None 
#   - left_index, right_index: bool
#   - sort: bool
#   - suffixes: different strings, including None
#   - indicator: False, True, or custom string
@given(st.data())
def test_merge(data):
    # Generate random left and right DataFrames or Series
    left = data.draw(st.one_of(
        st.builds(pd.DataFrame, 
            columns=st.lists(st.text(), min_size=1, max_size=10),
            index=st.one_of(st.just(None), st.lists(st.one_of(
                st.integers(), st.floats(), st.text(), st.booleans()), 
                unique=True, min_size=0, max_size=100)),
            data=st.lists(st.lists(st.one_of(
                st.none(), st.integers(), st.floats(), st.text(), st.booleans()),
                min_size=1, max_size=10), min_size=0, max_size=100)),
        st.builds(pd.Series,
            index=st.one_of(st.just(None), st.lists(st.one_of(
                st.integers(), st.floats(), st.text(), st.booleans()),
                unique=True, min_size=0, max_size=100)), 
            data=st.lists(st.one_of(
                st.none(), st.integers(), st.floats(), st.text(), st.booleans()),
                min_size=0, max_size=100))))
    
    right = data.draw(st.one_of(
        st.builds(pd.DataFrame,
            columns=st.lists(st.text(), min_size=1, max_size=10),
            index=st.one_of(st.just(None), st.lists(st.one_of(
                st.integers(), st.floats(), st.text(), st.booleans()),
                unique=True, min_size=0, max_size=100)),  
            data=st.lists(st.lists(st.one_of(
                st.none(), st.integers(), st.floats(), st.text(), st.booleans()),
                min_size=1, max_size=10), min_size=0, max_size=100)),
        st.builds(pd.Series,
            index=st.one_of(st.just(None), st.lists(st.one_of(
                st.integers(), st.floats(), st.text(), st.booleans()), 
                unique=True, min_size=0, max_size=100)),
            data=st.lists(st.one_of(
                st.none(), st.integers(), st.floats(), st.text(), st.booleans()),
                min_size=0, max_size=100))))

    # Generate random merge parameters 
    how = data.draw(st.sampled_from(['left', 'right', 'outer', 'inner', 'cross']))
    on = data.draw(st.one_of(st.none(), st.text(), st.lists(st.text())))
    left_on = data.draw(st.one_of(st.none(), st.text(), st.lists(st.text())))  
    right_on = data.draw(st.one_of(st.none(), st.text(), st.lists(st.text())))
    left_index = data.draw(st.booleans())
    right_index = data.draw(st.booleans())
    sort = data.draw(st.booleans())
    suffixes = data.draw(st.tuples(st.one_of(st.none(), st.text()), st.one_of(st.none(), st.text())))
    indicator = data.draw(st.one_of(st.just(False), st.just(True), st.text()))

    # Call merge with generated inputs
    result = pd.merge(left, right, how=how, on=on, left_on=left_on, right_on=right_on,
                      left_index=left_index, right_index=right_index, sort=sort, 
                      suffixes=suffixes, indicator=indicator)
    
    # Check properties that should hold for the merge result
    # 1. Result should be a DataFrame
    assert isinstance(result, pd.DataFrame)
    
    # 2. Number of rows should be >=0 and <= cartesian product of left and right rows
    assert 0 <= len(result) <= len(left) * len(right) 
    
    # 3. Number of columns should be >=1 and <= total columns in left and right 
    assert 1 <= len(result.columns) <= (len(left.columns) if isinstance(left, pd.DataFrame) else 1) + (len(right.columns) if isinstance(right, pd.DataFrame) else 1)

    # 4. No columns with duplicate names, except indicator column
    assert not any(result.columns.duplicated(keep=False)) or indicator != False

    # 5. Merging on index should keep index names, merging on columns should have default index
    if left_index or right_index:
        assert not result.index.name is None  
    else:
        assert result.index.name is None

    # 6. For how=left/right/inner, rows in result should be a subset of corresponding left/right rows
    if how in ['left', 'inner']: 
        assert result.drop(columns=result.columns.difference(left.columns), errors='ignore').apply(tuple, 1).isin(left.apply(tuple, 1)).all()
    if how in ['right', 'inner']:
        assert result.drop(columns=result.columns.difference(right.columns), errors='ignore').apply(tuple, 1).isin(right.apply(tuple, 1)).all()
   
    # 7. Indicator column should have only 'left_only', 'right_only', 'both' values
    if indicator:
        if isinstance(indicator, str):
            indicator_col = indicator
        else:
            indicator_col = '_merge'
        assert result[indicator_col].isin(['left_only','right_only','both']).all()
    
# End program