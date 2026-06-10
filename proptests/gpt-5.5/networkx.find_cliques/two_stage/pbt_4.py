from hypothesis import given, strategies as st
import networkx

MAX_NODES = 8


def draw_small_undirected_graph(data):
    n = data.draw(st.integers(min_value=0, max_value=MAX_NODES))
    possible_edges = [(i, j) for i in range(n) for j in range(i + 1, n)]

    if possible_edges:
        edges = data.draw(
            st.sets(st.sampled_from(possible_edges), max_size=len(possible_edges))
        )
    else:
        edges = set()

    G = networkx.Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from(edges)
    return G


def is_complete_subgraph(G, nodes):
    nodes = list(nodes)

    if len(nodes) != len(set(nodes)):
        return False

    if any(node not in G for node in nodes):
        return False

    for i, u in enumerate(nodes):
        for v in nodes[i + 1 :]:
            if not G.has_edge(u, v):
                return False

    return True


def is_maximal_clique(G, clique):
    clique_set = set(clique)

    if not is_complete_subgraph(G, clique):
        return False

    for node in G:
        if node not in clique_set:
            if all(G.has_edge(node, clique_node) for clique_node in clique_set):
                return False

    return True


def canonical_clique(clique):
    return tuple(sorted(clique))


def canonical_clique_set(cliques):
    return {canonical_clique(clique) for clique in cliques}


def brute_force_maximal_cliques(G):
    nodes = list(G.nodes)

    if not nodes:
        return []

    maximal_cliques = []

    for mask in range(1, 1 << len(nodes)):
        subset = [nodes[i] for i in range(len(nodes)) if mask & (1 << i)]

        if is_maximal_clique(G, subset):
            maximal_cliques.append(subset)

    return maximal_cliques


@given(st.data())
def test_networkx_find_cliques_property(data):
    G = draw_small_undirected_graph(data)

    cliques = list(networkx.find_cliques(G))
    expected_cliques = brute_force_maximal_cliques(G)

    for clique in cliques:
        assert isinstance(clique, list)
        assert len(clique) == len(set(clique))
        assert all(node in G for node in clique)
        assert is_complete_subgraph(G, clique)
        assert is_maximal_clique(G, clique)

    assert len(cliques) == len(canonical_clique_set(cliques))
    assert canonical_clique_set(cliques) == canonical_clique_set(expected_cliques)

    if expected_cliques:
        containing_clique = data.draw(st.sampled_from(expected_cliques))
        nodes = data.draw(
            st.lists(
                st.sampled_from(containing_clique),
                unique=True,
                max_size=len(containing_clique),
            )
        )
    else:
        nodes = []

    cliques_with_nodes = list(networkx.find_cliques(G, nodes=nodes))
    expected_cliques_with_nodes = [
        clique for clique in expected_cliques if set(nodes).issubset(clique)
    ]

    for clique in cliques_with_nodes:
        assert isinstance(clique, list)
        assert set(nodes).issubset(clique)
        assert is_complete_subgraph(G, clique)
        assert is_maximal_clique(G, clique)

    assert len(cliques_with_nodes) == len(canonical_clique_set(cliques_with_nodes))
    assert canonical_clique_set(cliques_with_nodes) == canonical_clique_set(
        expected_cliques_with_nodes
    )
# End program