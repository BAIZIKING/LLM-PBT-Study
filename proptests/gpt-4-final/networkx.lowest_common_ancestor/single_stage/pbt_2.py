from hypothesis import given, strategies as st
import networkx as nx

@given(st.data())
def test_lowest_common_ancestor(data):
    # generate the size of the graph
    graph_size = data.draw(st.integers(min_value=2, max_value=20))
    # generate a directed graph
    G = nx.gn_graph(graph_size)

    # pick two random nodes within the graph
    nodes = list(G.nodes())
    node1 = data.draw(st.sampled_from(nodes))
    node2 = data.draw(st.sampled_from(nodes))

    # compute the lowest common ancestor
    try:
        lca = nx.lowest_common_ancestor(G, node1, node2)
    except nx.NodeNotFound:
        assert False, "Node not found in the graph"
    except Exception as e:
        # unexpected exceptions
        assert False, f"Unexpected error: {str(e)}"
    
    # check that lca is in the ancestors of node1 and node2 if not default
    if lca is not None:
        assert lca in nx.ancestors(G, node1) and lca in nx.ancestors(G, node2), "Returned LCA is not an ancestor of the nodes"