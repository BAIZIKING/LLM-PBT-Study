from hypothesis import given, strategies as st
import networkx


def _draw_small_dag(data):
    n = data.draw(st.integers(min_value=1, max_value=12), label="number_of_nodes")
    nodes = list(range(n))

    possible_edges = [(u, v) for u in nodes for v in nodes if u < v]
    if possible_edges:
        edges = data.draw(
            st.lists(
                st.sampled_from(possible_edges),
                unique=True,
                max_size=min(40, len(possible_edges)),
            ),
            label="edges",
        )
    else:
        edges = []

    G = networkx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)

    node1 = data.draw(st.sampled_from(nodes), label="node1")
    node2 = data.draw(st.sampled_from(nodes), label="node2")

    return G, node1, node2


def _ancestors_including_self(G, node):
    return networkx.ancestors(G, node) | {node}


@given(st.data())
def test_networkx_lowest_common_ancestor_property(data):
    G, node1, node2 = _draw_small_dag(data)
    default = "__hypothesis_lca_default_sentinel__"

    result = networkx.lowest_common_ancestor(G, node1, node2, default=default)

    ancestors1 = _ancestors_including_self(G, node1)
    ancestors2 = _ancestors_including_self(G, node2)
    common_ancestors = ancestors1 & ancestors2

    # 1. The result is either the default value or a node in the graph.
    assert result == default or result in G

    if result != default:
        # 2. A non-default result is a common ancestor of both queried nodes.
        assert result in common_ancestors

        # 4. A non-default result is lowest: none of its proper descendants
        # is also a common ancestor of the queried nodes.
        assert not (networkx.descendants(G, result) & common_ancestors)
    else:
        # 3. The default is returned only when there are no common ancestors.
        assert not common_ancestors

    # 5. The result is symmetric in the two queried nodes.
    reversed_result = networkx.lowest_common_ancestor(
        G, node2, node1, default=default
    )
    assert reversed_result == result
# End program