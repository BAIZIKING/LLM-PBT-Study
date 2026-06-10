from hypothesis import given, strategies as st
import networkx as nx

# Summary: Generate random directed graphs with up to 100 nodes and 1000 edges. 
# The edge weights will be integers between -100 and 100.
# For each graph, generate a random subset of nodes to pass to degree().
# Check that:
# 1) The returned degree view is a dictionary
# 2) The keys of the degree view are the same as the nodes passed to degree()
# 3) The values of the degree view are non-negative integers
# 4) Passing weight=None gives the same result as the default
@given(
    st.builds(
        nx.gnm_random_graph,
        n=st.integers(min_value=0, max_value=100),  
        m=st.integers(min_value=0, max_value=1000),
        directed=st.booleans(),
    ).map(
        lambda G: nx.DiGraph(G) if st.booleans().example() else G
    ).map(
        lambda G: nx.DiGraph(
            (u, v, {'weight': w})
            for (u, v, w) in G.edges(data='weight', default=1)
        )
    ),
    st.lists(st.integers(min_value=0, max_value=99), unique=True),
)
def test_degree(G, nbunch):
    degrees = nx.degree(G, nbunch) 
    nbunch = set(nbunch).intersection(G)
    
    assert isinstance(degrees, dict)
    assert set(degrees.keys()) == set(nbunch if len(nbunch) > 0 else G.nodes)
    assert all(isinstance(d, int) and d >= 0 for d in degrees.values())
    assert nx.degree(G, nbunch, weight=None) == nx.degree(G, nbunch)
# End program