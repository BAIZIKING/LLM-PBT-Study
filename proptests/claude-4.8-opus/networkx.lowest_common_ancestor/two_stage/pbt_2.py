from hypothesis import given, strategies as st, settings, assume
import networkx as nx


# Strategy to build a random DAG (directed acyclic graph).
# We generate nodes 0..n-1 and only add edges from lower-index to higher-index
# nodes, which guarantees acyclicity. Node count is kept modest to avoid
# very large/expensive graphs.
@st.composite
def dags(draw):
    n = draw(st.integers(min_value=1, max_value=12))
    G = nx.DiGraph()
    G.add_nodes_from(range(n))
    # Possible edges (i, j) with i < j
    possible_edges = [(i, j) for i in range(n) for j in range(i + 1, n)]
    if possible_edges:
        edges = draw(
            st.lists(st.sampled_from(possible_edges), max_size=len(possible_edges))
        )
        G.add_edges_from(edges)
    return G


def ancestors_inclusive(G, node):
    """Return the set of ancestors of node, including node itself."""
    return nx.ancestors(G, node) | {node}


@given(st.data())
@settings(max_examples=300)
def test_networkx_lowest_common_ancestor_property():
    G = st.data
    data = G  # rename for clarity below

    # Re-acquire the data object properly (st.data() provides a draw interface).
    # The decorator passes a DataObject as the single argument; we capture it here.
    # (See the function signature handling below.)


# The above scaffolding does not match Hypothesis's calling convention.
# Re-define the test correctly with the DataObject parameter.

@given(st.data())
@settings(max_examples=300)
def test_networkx_lowest_common_ancestor_property(data):
    G = data.draw(dags())
    nodes = list(G.nodes())
    assume(len(nodes) >= 1)

    node1 = data.draw(st.sampled_from(nodes))
    node2 = data.draw(st.sampled_from(nodes))

    sentinel = object()  # unique default to detect "no common ancestor"
    result = nx.lowest_common_ancestor(G, node1, node2, default=sentinel)

    anc1 = ancestors_inclusive(G, node1)
    anc2 = ancestors_inclusive(G, node2)
    common = anc1 & anc2

    # Property 2: Default returned when no common ancestor exists.
    if not common:
        assert result is sentinel
        # Nothing else to check when there is no common ancestor.
        return
    else:
        assert result is not sentinel

    # Property 1: Ancestor of both nodes (or self).
    assert result in anc1
    assert result in anc2

    # Property 4: Lowest among common ancestors.
    # No other common ancestor should be a proper descendant of `result`.
    # Equivalently, none of result's proper descendants that are common
    # ancestors should exist; the result must be "lowest".
    descendants_of_result = nx.descendants(G, result)
    for c in common:
        if c == result:
            continue
        # If c is a proper descendant of result, then result was not the lowest.
        assert c not in descendants_of_result

    # Property 3: Symmetry of arguments.
    result_swapped = nx.lowest_common_ancestor(G, node2, node1, default=sentinel)
    assert result == result_swapped

    # Property 5: Self-LCA for identical nodes.
    if node1 == node2:
        assert result == node1
# End program