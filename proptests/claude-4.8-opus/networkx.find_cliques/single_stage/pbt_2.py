from hypothesis import given, strategies as st
import networkx as nx
from itertools import combinations

# Summary: Generate an undirected graph from a random node set and random edge
# set (including self-loops to test that they are ignored), with varying size
# and density. Then optionally generate a `nodes` subset (which may or may not
# form a clique) or None. Check that returned cliques are valid, are actual
# cliques, are maximal, contain the requested `nodes`, and that a non-clique
# `nodes` raises ValueError; also verify full coverage when nodes is None.
@given(st.data())
def test_networkx_find_cliques(data):
    n = data.draw(st.integers(min_value=0, max_value=8), label="num_nodes")
    nodes = list(range(n))

    # Generate edges (including possible self-loops to test they are ignored).
    possible_edges = [(u, v) for u in nodes for v in nodes if u <= v]
    if possible_edges:
        chosen = data.draw(
            st.lists(st.sampled_from(possible_edges), unique=True),
            label="edges",
        )
    else:
        chosen = []

    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(chosen)

    # Decide whether to pass a `nodes` argument.
    use_nodes = data.draw(st.booleans(), label="use_nodes")
    requested = None
    if use_nodes and nodes:
        requested = data.draw(
            st.lists(st.sampled_from(nodes), unique=True, max_size=n),
            label="requested_nodes",
        )

    def is_clique(node_list):
        for a, b in combinations(node_list, 2):
            if not G.has_edge(a, b):
                return False
        return True

    # If `requested` is a non-empty set that is NOT a clique, expect ValueError.
    if requested:
        if not is_clique(requested):
            try:
                list(nx.find_cliques(G, nodes=requested))
                assert False, "Expected ValueError for non-clique nodes"
            except ValueError:
                return  # Correct behavior; nothing more to check.

    cliques = list(nx.find_cliques(G, nodes=requested))

    all_clique_members = set()
    for clique in cliques:
        # Property 1: clique is a list of nodes in G.
        assert isinstance(clique, list)
        for v in clique:
            assert v in G

        # Property 2: it is an actual clique (ignoring self-loops; combinations
        # only considers distinct pairs).
        assert is_clique(clique)

        # Property 3: maximality - no other node is adjacent to all members.
        clique_set = set(clique)
        for v in G.nodes():
            if v in clique_set:
                continue
            adjacent_to_all = all(G.has_edge(v, u) for u in clique)
            assert not adjacent_to_all, f"Clique {clique} not maximal w.r.t {v}"

        # Property 4: returned cliques contain all requested nodes.
        if requested:
            assert set(requested).issubset(clique_set)

        all_clique_members.update(clique_set)

    # Property 7: when nodes is None and G is non-empty, every node appears in
    # at least one maximal clique.
    if requested is None and n > 0:
        assert all_clique_members == set(nodes)
# End program