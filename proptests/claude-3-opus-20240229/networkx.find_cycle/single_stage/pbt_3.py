from hypothesis import given, strategies as st
import networkx as nx

# Summary: 
# Generate random directed/undirected graphs and multigraphs with various numbers of nodes and edges.
# Test edge cases by sometimes generating empty graphs, DAGs, self-loops, and parallel edges.
# Generate all possible combinations of the orientation parameter.
# Check that find_cycle either returns a valid cycle or raises NetworkXNoCycle.
# For cycles found, check that the edges form a path and a cycle.
# Check that the orientation of the edges is respected based on the orientation parameter.
@given(st.data())
def test_find_cycle(data):
    # Generate random graph parameters
    n_nodes = data.draw(st.integers(min_value=0, max_value=10))
    n_edges = data.draw(st.integers(min_value=0, max_value=n_nodes * (n_nodes - 1) // 2))
    is_directed = data.draw(st.booleans())
    is_multigraph = data.draw(st.booleans())
    
    # Generate random graph
    if is_multigraph:
        if is_directed:
            G = nx.MultiDiGraph()
        else:
            G = nx.MultiGraph()
    else:
        if is_directed:
            G = nx.DiGraph()
        else:
            G = nx.Graph()
    
    nodes = range(n_nodes)
    G.add_nodes_from(nodes)
    
    # Add random edges
    possible_edges = [(u, v) for u in nodes for v in nodes if u != v]
    edges = data.draw(st.lists(st.sampled_from(possible_edges), min_size=n_edges, max_size=n_edges, unique=True))
    G.add_edges_from(edges)
    
    # Randomly add self-loops and parallel edges for edge cases
    if is_multigraph:
        G.add_edges_from((u, u) for u in data.draw(st.lists(st.sampled_from(nodes), unique=True)))
        G.add_edges_from(data.draw(st.lists(st.sampled_from(edges), unique=True)))
    
    # Generate orientation parameter
    orientation = data.draw(st.one_of(st.none(), st.sampled_from(['original', 'reverse', 'ignore'])))
    
    # Run find_cycle
    try:
        cycle = nx.find_cycle(G, orientation=orientation)
        # Check that a cycle was found
        assert cycle
        
        # Check that the edges form a path
        for i in range(len(cycle) - 1):
            assert cycle[i][1] == cycle[i+1][0]
        
        # Check that the edges form a cycle
        assert cycle[0][0] == cycle[-1][1]
        
        # Check the orientation of the edges
        if orientation is not None:
            for u, v, *o in cycle:
                if orientation == 'original':
                    assert G.has_edge(u, v)
                elif orientation == 'reverse':
                    assert G.has_edge(v, u)
    
    except nx.NetworkXNoCycle:
        # Check that an exception is raised if no cycle exists
        assert not any(nx.simple_cycles(G))
# End program