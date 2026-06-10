from hypothesis import given, settings, strategies as st
import networkx
from itertools import combinations


@st.composite
def graphs(draw, max_nodes=8):
    n = draw(st.integers(min_value=0, max_value=max_nodes))
    nodes = list(range(n))
    possible_edges = list(combinations(nodes, 2))
    if possible_edges:
        chosen = draw(st.lists(st.sampled_from(possible_edges),
                               max_size=len(possible_edges)))
    else:
        chosen = []
    G = networkx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(chosen)
    return G


def is_clique(G, clique):
    for u, v in combinations(clique, 2):
        if not G.has_edge(u, v):
            return False
    return True


@given(st.data())
@settings(max_examples=300)
def test_networkx_find_cliques_property(data):
    G = data.draw(graphs())

    cliques = list(networkx.find_cliques(G))

    # ---- Property 1: Every returned clique is a valid clique. ----
    for c in cliques:
        assert is_clique(G, c), f"{c} is not a valid clique"

    # ---- Property 2: Every returned clique is maximal. ----
    for c in cliques:
        cset = set(c)
        for node in G.nodes():
            if node in cset:
                continue
            # node should NOT be adjacent to every member of c
            if all(G.has_edge(node, m) for m in c):
                assert False, f"{c} is not maximal, can add {node}"

    # ---- Property 3: nodes constraint and ValueError behaviour. ----
    node_list = list(G.nodes())
    if node_list:
        # Pick a subset to use as `nodes`.
        subset = data.draw(st.lists(st.sampled_from(node_list),
                                    max_size=min(4, len(node_list)),
                                    unique=True))
        if is_clique(G, subset):
            constrained = list(networkx.find_cliques(G, nodes=subset))
            for c in constrained:
                assert set(subset).issubset(set(c)), (
                    f"{c} does not contain required nodes {subset}")
                assert is_clique(G, c)
        else:
            # subset is not a clique -> ValueError expected.
            try:
                list(networkx.find_cliques(G, nodes=subset))
                assert False, "Expected ValueError for non-clique nodes"
            except ValueError:
                pass

    # ---- Property 4: Completeness and non-redundancy. ----
    # No duplicate cliques (as frozensets).
    frozen = [frozenset(c) for c in cliques]
    assert len(frozen) == len(set(frozen)), "Duplicate cliques returned"

    # Compare against recursive reference implementation for completeness.
    reference = list(networkx.find_cliques_recursive(G))
    ref_frozen = set(frozenset(c) for c in reference)
    assert set(frozen) == ref_frozen, (
        "Set of maximal cliques differs from reference implementation")

    # ---- Property 5: nodes are in G; self-loops/parallel edges ignored. ----
    for c in cliques:
        for node in c:
            assert node in G, f"{node} not in graph"

    # Build a copy with self-loops added; result must be identical.
    H = G.copy()
    for node in G.nodes():
        H.add_edge(node, node)  # self-loop
    h_cliques = set(frozenset(c) for c in networkx.find_cliques(H))
    assert h_cliques == set(frozen), (
        "Self-loops changed the set of maximal cliques")
# End program