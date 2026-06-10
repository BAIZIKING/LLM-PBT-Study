from hypothesis import given, strategies as st, settings
import networkx
from itertools import combinations


@st.composite
def graphs(draw, max_nodes=8):
    n = draw(st.integers(min_value=0, max_value=max_nodes))
    nodes = list(range(n))
    possible_edges = list(combinations(nodes, 2))
    if possible_edges:
        edges = draw(
            st.lists(st.sampled_from(possible_edges), max_size=len(possible_edges))
        )
    else:
        edges = []
    G = networkx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    return G


def is_clique(G, clique):
    return all(G.has_edge(u, v) for u, v in combinations(clique, 2))


@given(st.data())
@settings(max_examples=200)
def test_networkx_find_cliques_property(data):
    G = data.draw(graphs())
    cliques = list(networkx.find_cliques(G))

    # Property 1: Every returned clique is a valid clique in G.
    for c in cliques:
        assert is_clique(G, c), f"Returned set {c} is not a valid clique"

    # Property 2: Every returned clique is maximal.
    for c in cliques:
        cset = set(c)
        for n in G.nodes():
            if n in cset:
                continue
            if all(G.has_edge(n, m) for m in c):
                assert False, f"Clique {c} is not maximal; node {n} addable"

    # Property 4: Union of all cliques covers every node of G.
    covered = set()
    for c in cliques:
        covered.update(c)
    assert covered == set(G.nodes()), "Cliques do not cover all nodes"

    # Property 3: nodes argument behavior.
    if cliques:
        # Pick a known valid clique and check all returned cliques contain it.
        sub = data.draw(st.sampled_from(cliques))
        # Use a subset of an actual clique -> guaranteed valid clique input
        if sub:
            k = data.draw(st.integers(min_value=1, max_value=len(sub)))
            req = sub[:k]
            constrained = list(networkx.find_cliques(G, nodes=req))
            for c in constrained:
                assert set(req).issubset(set(c)), (
                    f"Clique {c} does not contain required nodes {req}"
                )
            for c in constrained:
                assert is_clique(G, c)

    # Property 3b: Non-clique nodes raise ValueError.
    non_edges = [
        [u, v] for u, v in combinations(G.nodes(), 2) if not G.has_edge(u, v)
    ]
    if non_edges:
        bad = data.draw(st.sampled_from(non_edges))
        try:
            list(networkx.find_cliques(G, nodes=list(bad)))
            assert False, "Expected ValueError for non-clique nodes"
        except ValueError:
            pass

    # Property 5: Self-loops and parallel edges are ignored.
    H = networkx.Graph(G)  # copy
    for n in list(H.nodes()):
        H.add_edge(n, n)  # add self loops
    cliques_H = sorted(sorted(c) for c in networkx.find_cliques(H))
    cliques_G = sorted(sorted(c) for c in networkx.find_cliques(G))
    assert cliques_H == cliques_G, "Self-loops changed the set of maximal cliques"
# End program