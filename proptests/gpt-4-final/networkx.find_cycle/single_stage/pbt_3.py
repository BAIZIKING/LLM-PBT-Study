from hypothesis import given, strategies as st, assume
import networkx as nx

@given(st.data())
def test_find_cycle(data):
    # Generate a list of nodes
    nodes = data.draw(st.lists(st.integers(min_value=0, max_value=5), min_size=2, max_size=5, unique=True))
    # Generate a list of edges
    edges = data.draw(st.lists(st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)).filter(lambda edge: edge[0] != edge[1]), min_size=0, max_size=10, unique=True))
    
    # Create a graph and add edges
    G = nx.DiGraph()
    G.add_edges_from(edges)
    
    # Randomly select a source node
    source = data.draw(st.one_of(st.sampled_from(nodes), st.none()))
    
    # Select an orientation randomly
    orientation = data.draw(st.sampled_from(['original', 'reverse', 'ignore', None]))
    
    try:
        cycle = nx.find_cycle(G, source=source, orientation=orientation)
        assert cycle in nx.simple_cycles(G)
    except nx.NetworkXNoCycle:
        assert len(list(nx.cycles.simple_cycles(G))) == 0
# End program