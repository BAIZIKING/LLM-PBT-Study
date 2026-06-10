from hypothesis import given, strategies as st
import networkx as nx

# Summary: 
# Generate directed and undirected graphs, with varying node counts, edge counts, and edge orientations
# Check that:
# - An exception is raised if no cycle exists
# - If a cycle is found, it is returned as a list of edges that form a cycle
# - The source node is included in the cycle if specified
# - Edges in the cycle follow the specified orientation
@given(
    graph_type=st.sampled_from([nx.Graph, nx.DiGraph]),
    nodes=st.integers(min_value=2, max_value=100),
    edge_prob=st.floats(min_value=0.1, max_value=1.0),
    source=st.one_of(st.none(), st.integers()),
    orientation=st.sampled_from([None, 'original', 'reverse', 'ignore'])
)
def test_find_cycle(graph_type, nodes, edge_prob, source, orientation):
    G = nx.gnp_random_graph(nodes, edge_prob, directed=(graph_type==nx.DiGraph))
    
    if source is not None:
        source = source % nodes
    
    try:
        cycle = nx.find_cycle(G, source=source, orientation=orientation)
        assert len(cycle) >= 2
        assert all(u in G and v in G for u, v, *_ in cycle)
        if source is not None:
            assert source in {u for u, v, *_ in cycle} or source in {v for u, v, *_ in cycle}
        if orientation is not None:
            assert all(w == 'forward' or w == 'reverse' for _, _, *w in cycle)
    except nx.NetworkXNoCycle:
        assert not any(nx.simple_cycles(G))
# End program