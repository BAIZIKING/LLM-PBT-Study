from hypothesis import given, strategies as st
import networkx as nx

@given(st.lists(st.integers(), min_size=2, max_size=10), st.integers(), st.integers(), st.integers())
def test_networkx_lowest_common_ancestor_idempotency(nodes, node1, node2, default):
    G = nx.DiGraph()
    nx.add_path(G, nodes)
    assert nx.lowest_common_ancestor(G, node1, node2, default) == nx.lowest_common_ancestor(G, node1, node2, default)

@given(st.lists(st.integers(), min_size=2, max_size=10), st.integers(), st.integers(), st.integers())
def test_networkx_lowest_common_ancestor_consistency(nodes, node1, node2, default):
    G = nx.DiGraph()
    nx.add_path(G, nodes)
    assert nx.lowest_common_ancestor(G, node1, node2, default) == nx.lowest_common_ancestor(G, node2, node1, default)

@given(st.lists(st.integers(), min_size=2, max_size=10), st.integers(), st.integers(), st.integers())
def test_networkx_lowest_common_ancestor_node_presence(nodes, node1, node2, default):
    G = nx.DiGraph()
    nx.add_path(G, nodes)
    if node1 not in nodes or node2 not in nodes:
        assert nx.lowest_common_ancestor(G, node1, node2, default) == default

@given(st.lists(st.integers(), min_size=2, max_size=10), st.integers(), st.integers(), st.integers())
def test_networkx_lowest_common_ancestor_topology_constraint(nodes, node1, node2, default):
    G = nx.DiGraph()
    nx.add_path(G, nodes)
    if nodes[0] == node1 or nodes[0]==node2:
        assert nx.lowest_common_ancestor(G, node1, node2, default) == nodes[0]

@given(st.lists(st.integers(), min_size=2, max_size=10), st.integers(), st.integers(), st.integers())
def test_networkx_lowest_common_ancestor_default_value_constraint(nodes, node1, node2, default):
    G = nx.DiGraph()
    nx.add_path(G, nodes)
    common_ancestors = set(nx.ancestors(G, node1)) & set(nx.ancestors(G, node2))
    if len(common_ancestors)==0:
        assert nx.lowest_common_ancestor(G, node1, node2, default) == default
# End program