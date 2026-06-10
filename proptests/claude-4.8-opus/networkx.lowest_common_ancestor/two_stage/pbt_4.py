from hypothesis import given, strategies as st, settings, assume
import networkx as nx


@st.composite
def dags(draw):
    # Build a random DAG with small node count to avoid very large inputs.
    n = draw(st.integers(min_value=1, max_value=8))
    G = nx.DiGraph()
    G.add_nodes_from(range(n))
    for i in range(n):
        for j in range(i + 1, n):
            if draw(st.booleans()):
                G.add_edge(i, j)
    return G


def common_ancestors(G, node1, node2):
    anc1 = nx.ancestors(G, node1) | {node1}
    anc2 = nx.ancestors(G, node2) | {node2}
    return anc1 & anc2


# Property 1: Ancestor validity
@settings(max_examples=300)
@given(st.data())
def test_networkx_lowest_common_ancestor_ancestor_validity(data):
    G = data.draw(dags())
    node1 = data.draw(st.sampled_from(list(G.nodes())))
    node2 = data.draw(st.sampled_from(list(G.nodes())))
    sentinel = object()
    result = nx.lowest_common_ancestor(G, node1, node2, default=sentinel)
    if result is not sentinel:
        # result must be an ancestor-or-self of both nodes
        assert nx.has_path(G, result, node1)
        assert nx.has_path(G, result, node2)
# End program


# Property 2: Lowest/Maximal property
@settings(max_examples=300)
@given(st.data())
def test_networkx_lowest_common_ancestor_lowest_property(data):
    G = data.draw(dags())
    node1 = data.draw(st.sampled_from(list(G.nodes())))
    node2 = data.draw(st.sampled_from(list(G.nodes())))
    sentinel = object()
    result = nx.lowest_common_ancestor(G, node1, node2, default=sentinel)
    if result is not sentinel:
        commons = common_ancestors(G, node1, node2)
        # No strict descendant of result is also a common ancestor.
        descendants = nx.descendants(G, result)
        for c in commons:
            if c in descendants:  # c is a strict descendant of result
                assert False, (
                    f"{c} is a common ancestor strictly below result {result}"
                )
# End program


# Property 3: Symmetry
@settings(max_examples=300)
@given(st.data())
def test_networkx_lowest_common_ancestor_symmetry(data):
    G = data.draw(dags())
    node1 = data.draw(st.sampled_from(list(G.nodes())))
    node2 = data.draw(st.sampled_from(list(G.nodes())))
    sentinel = object()
    r1 = nx.lowest_common_ancestor(G, node1, node2, default=sentinel)
    r2 = nx.lowest_common_ancestor(G, node2, node1, default=sentinel)
    assert r1 == r2
# End program


# Property 4: Reflexivity / self-ancestry
@settings(max_examples=300)
@given(st.data())
def test_networkx_lowest_common_ancestor_reflexivity(data):
    G = data.draw(dags())
    node = data.draw(st.sampled_from(list(G.nodes())))
    result = nx.lowest_common_ancestor(G, node, node, default=None)
    assert result == node
# End program


# Property 5: Default fallback correctness
@settings(max_examples=300)
@given(st.data())
def test_networkx_lowest_common_ancestor_default_fallback(data):
    G = data.draw(dags())
    node1 = data.draw(st.sampled_from(list(G.nodes())))
    node2 = data.draw(st.sampled_from(list(G.nodes())))
    sentinel = object()
    result = nx.lowest_common_ancestor(G, node1, node2, default=sentinel)
    commons = common_ancestors(G, node1, node2)
    if commons:
        # There is at least one common ancestor: result must be one of them.
        assert result is not sentinel
        assert result in commons
    else:
        # No common ancestor: must return the default sentinel.
        assert result is sentinel
# End program