from hypothesis import given, strategies as st
import networkx as nx

# First, define a simple strategy for generating directed graph
def graph_strategy():
    return st.dictionaries(
        keys=st.integers(min_value=0, max_value=20),
        values=st.lists(st.integers(min_value=0, max_value=20)),
        min_size=1,
        max_size=20
    ).map(nx.DiGraph)

@given(graph_strategy(), st.integers(min_value=0, max_value=20), st.integers(min_value=0, max_value=20))
def test_networkx_lowest_common_ancestor_property(graph, node1, node2):
    # Assume node1 and node2 are in the graph
    if node1 not in graph.nodes or node2 not in graph.nodes:
        return

    # Compute the LCA
    lca = nx.lowest_common_ancestor(graph, node1, node2)

    # 1. Output node is ancestor of both node1 and node2
    assert lca in nx.ancestors(graph, node1)
    assert lca in nx.ancestors(graph, node2)

    # 3. Output should be lowest
    for node in graph.nodes:
        if node in nx.ancestors(graph, node1) and node in nx.ancestors(graph, node2):
            assert not nx.has_path(graph, lca, node)

    # 5. Consistent output
    assert nx.lowest_common_ancestor(graph, node1, node2) == lca

@given(graph_strategy(), st.integers(min_value=0, max_value=20), st.integers(min_value=0, max_value=20), st.integers())
def test_networkx_lowest_common_ancestor_default_property(graph, node1, node2, default):
    # Assume node1 and node2 are in the graph
    if node1 not in graph.nodes or node2 not in graph.nodes:
        return
    
    # 4. Output should be default if no common ancestor exists
    common_ancestors = set(nx.ancestors(graph, node1)).intersection(nx.ancestors(graph, node2))
    if len(common_ancestors) == 0:
        assert nx.lowest_common_ancestor(graph, node1, node2, default=default) == default

# End program