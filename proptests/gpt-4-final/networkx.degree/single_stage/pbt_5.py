from hypothesis import given, strategies as st
import networkx as nx

@given(st.one_of(st.none(), st.lists(st.integers(min_value=0, max_value=100), min_size=1, max_size=100)))
def test_networkx_degree(nbunch):
    G = nx.path_graph(101) # create a graph with 101 nodes
    degree_view = nx.degree(G, nbunch)
    for _, degree in degree_view:
        assert isinstance(degree, int) # Check type
        assert degree >= 0 # Check that degree is non-negative
# End program
