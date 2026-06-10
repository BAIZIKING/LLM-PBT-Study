from hypothesis import given, strategies as st
import networkx as nx
from itertools import combinations

# Summary: Generate small undirected Graph/MultiGraph inputs, including empty graphs,
# isolated nodes, arbitrary edge sets, self-loops, and duplicate/parallel edges.
# Also generate nodes=None or a unique list of existing nodes, which may or may not
# itself form a clique. Check that non-clique node lists raise ValueError; otherwise,
# every returned clique is complete, maximal, contains the requested nodes, and matches
# a brute-force enumeration of all maximal cliques while ignoring self-loops/parallel edges.
@given(st.data())
def test_networkx_find_cliques(data):
    graph_type = data.draw(st.sampled_from([nx.Graph, nx.MultiGraph]), label="graph_type")
    n = data.draw(st.integers(min_value=0, max_value=8), label="node_count")

    G = graph_type()
    G.add_nodes_from(range(n))

    normal_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    self_loops = [(u, u) for u in range(n)]
    all_possible_edges = normal_edges + self_loops

    if normal_edges:
        chosen_edges = data.draw(
            st.sets(st.sampled_from(normal_edges), max_size=len(normal_edges)),
            label="chosen_edges",
        )
        G.add_edges_from(chosen_edges)

    if self_loops:
        chosen_loops = data.draw(
            st.sets(st.sampled_from(self_loops), max_size=len(self_loops)),
            label="chosen_self_loops",
        )
        G.add_edges_from(chosen_loops)

    if all_possible_edges:
        extra_edges = data.draw(
            st.lists(st.sampled_from(all_possible_edges), max_size=12),
            label="extra_duplicate_or_parallel_edges",
        )
        G.add_edges_from(extra_edges)

    if n == 0:
        nodes_arg = data.draw(st.one_of(st.none(), st.just([])), label="nodes")
    else:
        nodes_arg = data.draw(
            st.one_of(
                st.none(),
                st.lists(st.sampled_from(list(range(n))), unique=True, max_size=n),
            ),
            label="nodes",
        )

    adjacency = {u: set(G[u]) - {u} for u in G}

    def is_complete(vertices):
        vertices = list(vertices)
        return all(v in adjacency[u] for u, v in combinations(vertices, 2))

    def is_maximal(vertices):
        vertices = set(vertices)
        for candidate in set(G) - vertices:
            if all(candidate in adjacency[u] for u in vertices):
                return False
        return True

    query_is_clique = nodes_arg is None or is_complete(nodes_arg)

    if not query_is_clique:
        try:
            list(nx.find_cliques(G, nodes=nodes_arg))
        except ValueError:
            return
        assert False, "find_cliques should raise ValueError when nodes is not a clique"

    result = list(nx.find_cliques(G, nodes=nodes_arg))

    for clique in result:
        assert isinstance(clique, list)
        assert set(clique).issubset(set(G))
        assert is_complete(clique)
        assert is_maximal(clique)
        if nodes_arg is not None:
            assert set(nodes_arg).issubset(set(clique))

    result_sets = {frozenset(clique) for clique in result}
    assert len(result_sets) == len(result)

    expected_sets = set()
    graph_nodes = list(G)

    for size in range(1, len(graph_nodes) + 1):
        for candidate in combinations(graph_nodes, size):
            if is_complete(candidate) and is_maximal(candidate):
                expected_sets.add(frozenset(candidate))

    if nodes_arg is not None:
        requested = set(nodes_arg)
        expected_sets = {
            clique for clique in expected_sets if requested.issubset(clique)
        }

    assert result_sets == expected_sets

# End program