from hypothesis import given, strategies as st
import networkx as nx

# Strategy: Generate directed graph with varying number of nodes and edges.
# Also generate node1 and node2 from nodes within the graph, and default parameter as any Python's built in types
@given(st.data())
def test_lowest_common_ancestor(data):
    # Generate graph with varying number of nodes and edges
    nodes = data.draw(st.lists(st.integers(), min_size=2, unique=True))
    edges = data.draw(st.lists(st.tuples(st.sampled_from(nodes), st.sampled_from(nodes))))
    
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    
    # Generate node1 and node2 from nodes within the graph
    node1 = data.draw(st.sampled_from(nodes))
    nodes.remove(node1)
    node2 = data.draw(st.sampled_from(nodes))
    
    # Generate default parameter as any Python's built in types
    default = data.draw(st.one_of(st.integers(), st.text(), st.floats()))

    # Calculate Lowest common ancestor
    result = nx.lowest_common_ancestor(G, node1, node2, default=default)

    # Check if result is actually a common ancestor or the default value
    ancestors1 = nx.ancestors(G, node1)
    ancestors2 = nx.ancestors(G, node2)
    common_ancestors = ancestors1 & ancestors2

    if len(common_ancestors) > 0:
        # If ancestors found, check if result is in ancestors
        assert result in common_ancestors
    else:
        #If no ancestors, check if result equals default
        assert result == default