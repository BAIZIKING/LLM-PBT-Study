from hypothesis import given, settings, strategies as st
from itertools import combinations
import networkx


@st.composite
def graphs(draw):
    n = draw(st.integers(min_value=0, max_value=8))
    nodes = list(range(n))
    possible_edges = list(combinations(nodes, 2))
    if possible_edges:
        edges = draw(
            st.lists(
                st.sampled_from(possible_edges),
                max_size=len(possible_edges),
                unique=True,
            )
        )
    else:
        edges = []
    G = networkx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    return G


def is_complete(G, clique):
    for u, v in combinations(clique, 2):
        if not G.has_edge(u, v):
            return False
    return True


@given(st.data())
@settings(deadline=None)
def test_networkx_find_cliques_property(data):
    G = data.draw(graphs())
    cliques = list(networkx.find_cliques(G))

    # Property 1: Every clique is a complete subgraph of G.
    for clique in cliques:
        assert is_complete(G, clique), f"Clique {clique} is not complete"

    # Property 2: Every clique is maximal (cannot be extended).
    clique_sets = [set(c) for c in cliques]
    for cset in clique_sets:
        for node in G.nodes():
            if node in cset:
                continue
            if all(G.has_edge(node, c) for c in cset):
                assert False, f"Clique {cset} can be extended by {node}"

    # Property 3: Cliques contain only existing nodes and no duplicates.
    node_set = set(G.nodes())
    for clique in cliques:
        assert len(clique) == len(set(clique)), f"Duplicate nodes in {clique}"
        for node in clique:
            assert node in node_set, f"Node {node} not in graph"

    # Property 4: nodes argument behavior.
    nodelist = list(G.nodes())
    if nodelist:
        # pick a subset that forms a clique: choose a single node (always a clique)
        chosen = [data.draw(st.sampled_from(nodelist))]
        result = list(networkx.find_cliques(G, nodes=chosen))
        for clique in result:
            assert set(chosen).issubset(set(clique)), \
                f"Clique {clique} does not contain required nodes {chosen}"

        # Pick a pair that is NOT a clique (non-edge) and expect ValueError
        non_edges = [
            (u, v) for u, v in combinations(nodelist, 2) if not G.has_edge(u, v)
        ]
        if non_edges:
            bad_pair = data.draw(st.sampled_from(non_edges))
            try:
                list(networkx.find_cliques(G, nodes=list(bad_pair)))
                assert False, f"Expected ValueError for non-clique {bad_pair}"
            except ValueError:
                pass

    # Property 5: Every node is covered, no duplicate cliques, no clique subset of another.
    covered = set()
    for cset in clique_sets:
        covered |= cset
    assert covered == node_set, "Not all nodes are covered by cliques"

    # No duplicate cliques
    frozen = [frozenset(c) for c in clique_sets]
    assert len(frozen) == len(set(frozen)), "Duplicate cliques found"

    # No clique is a strict subset of another
    for i, a in enumerate(clique_sets):
        for j, b in enumerate(clique_sets):
            if i != j:
                assert not a < b, f"Clique {a} is a strict subset of {b}"
# End program