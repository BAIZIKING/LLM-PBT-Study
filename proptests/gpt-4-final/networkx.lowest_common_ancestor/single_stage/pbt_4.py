from hypothesis import given, strategies as st
import networkx as nx

# Strategy: Draw a list to represent a graph and two nodes from that list.
@given(st.data())
def test_networkx_lowest_common_ancestor(data):
    # We generate a random graph by first drawing a list of nodes.
    nodes = data.draw(st.lists(st.integers(min_value=0, max_value=100), min_size=2, unique=True))
    # We then generate a directed graph from this list.
    G = nx.DiGraph()
    nx.add_path(G, nodes)
    
    # We pick two random nodes from the graph.
    node1 = data.draw(st.sampled_from(nodes))
    nodes.remove(node1)
    node2 = data.draw(st.sampled_from(nodes))
    
    # Draw a default value
    default = data.draw(st.integers())

    # We don't expect the function to raise an error on valid inputs.
    try:
        result = nx.lowest_common_ancestor(G, node1, node2, default)

        # The result should be a common ancestor if it exists, or the default value.
        ancestors = nx.ancestors(G, node1).intersection(
                        nx.ancestors(G, node2)
                    )
        assert result in ancestors or result == default
    except Exception as e:
        assert False, f"Unexpected error: {e}"