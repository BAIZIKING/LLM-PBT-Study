from hypothesis import given, strategies as st
import networkx as nx

# Summary: 
# - Generate a random graph using hypothesis' graph strategy
# - Randomly decide whether to make it a directed or undirected graph
# - Optionally add some extra random edges to introduce cycles
# - Choose a random orientation parameter
# - Call find_cycle and check properties of the result
@given(
    G=st.graphs(min_vertices=0, max_vertices=20),  
    is_directed=st.booleans(),
    extra_edges=st.lists(st.tuples(st.integers(min_value=0, max_value=19), st.integers(min_value=0, max_value=19)), max_size=10),
    orientation=st.one_of(st.none(), st.sampled_from(['original', 'reverse', 'ignore']))
)
def test_find_cycle(G, is_directed, extra_edges, orientation):
    if is_directed:
        G = G.to_directed()
    else:
        G = G.to_undirected()
    
    G.add_edges_from(extra_edges)
    
    try:
        cycle = nx.find_cycle(G, orientation=orientation)
        
        if orientation is None:
            # Check cycle is valid
            assert len(cycle) > 1
            assert cycle[0][0] == cycle[-1][1]
        else:
            # Check extended edge tuples are returned with correct orientation
            assert len(cycle[0]) == 3
            assert cycle[0][2] in ['forward', 'reverse']

            # Check cycle is valid
            if orientation == 'ignore':
                assert cycle[0][0] == cycle[-1][1]
            else:
                assert cycle[0][0] == cycle[-1][1] and cycle[0][2] == 'reverse'

    except nx.NetworkXNoCycle:
        # Check that an exception is only raised if there is no cycle
        assert nx.is_directed_acyclic_graph(G) or nx.is_forest(G)
# End program