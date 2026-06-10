from hypothesis import given, strategies as st
import networkx as nx

# Summary: 
# - Generate a random directed graph with between 2-100 nodes
# - Generate 2 random nodes from the graph 
# - Add one or more paths between the nodes to create a common ancestor
# - Check that lowest_common_ancestor returns a valid common ancestor node
# - Check that returning the ancestor and traversing to each input node is valid
# - Check that default is returned if no paths added between nodes
@given(
    G=st.builds(nx.DiGraph), 
    num_nodes=st.integers(min_value=2, max_value=100),
    paths=st.lists(st.lists(st.integers(), min_size=2), min_size=0),
    default=st.one_of(st.none(), st.integers(), st.text())
)
def test_lowest_common_ancestor(G, num_nodes, paths, default):
    G.add_nodes_from(range(num_nodes))

    nodes = st.sampled_from(list(G.nodes))
    node1 = nodes.example()
    assume(node1 in G)
    node2 = nodes.filter(lambda n: n != node1).example()
    assume(node2 in G)

    for path in paths:
        nx.add_path(G, path)

    ancestor = nx.lowest_common_ancestor(G, node1, node2, default)

    if ancestor is None:
        assert not nx.has_path(G, node1, node2) 
        assert not nx.has_path(G, node2, node1)
    elif ancestor == default:
        assert not nx.has_path(G, node1, node2)
        assert not nx.has_path(G, node2, node1)
    else:
        assert nx.has_path(G, ancestor, node1)
        assert nx.has_path(G, ancestor, node2)
# End program