from hypothesis import given, strategies as st
import itertools
import networkx as nx

# Generate nodes, edges, a source node and orientation for networkx.find_cycle()
@given(st.data())
def test_find_cycle(data):
    num_nodes = data.draw(st.integers(min_value=0, max_value=50))
    nodes = list(range(num_nodes))
    edges = list(itertools.combinations(nodes, 2))
    source = data.draw(st.one_of(st.none(), st.sampled_from(nodes)), label="source")
    orientation = data.draw(st.one_of(st.none(), st.sampled_from(['original', 'reverse', 'ignore'])), label="orientation")
    
    # generate a graph
    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    
    # verify the properties
    try:
        cycle = nx.find_cycle(G, source=source, orientation=orientation)
        assert len(cycle) >= 3  # At least a simple cycle (triangle)
    except nx.exception.NetworkXNoCycle:
        assert nx.number_of_edges(G) < num_nodes  # The graph doesn't have enough edges to form a cycle