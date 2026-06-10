from hypothesis import given, strategies as st
import networkx as nx
from itertools import combinations

# Summary: Generate a random set of integer nodes, then randomly select edges
# (allowing self-loops to test that they are ignored). Build an undirected
# nx.Graph. Then with some probability pass `nodes` as None, a known clique
# (subset of a maximal clique) to test filtering, or an arbitrary node subset
# to potentially trigger the ValueError path. Verify maximality, clique-ness,
# membership validity, coverage, and the `nodes` filtering / ValueError behavior.
@given(st.data())
def test_networkx_find_cliques(data):
    n = data.draw(st.integers(min_value=0, max_value=8), label="num_nodes")
    nodes = list(range(n))

    possible_edges = list(combinations(nodes, 2)) + [(v, v) for v in nodes]
    chosen = data.draw(
        st.lists(st.sampled_from(possible_edges) if possible_edges else st.nothing(),
                 max_size=len(possible_edges)),
        label="edges",
    ) if possible_edges else []

    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(chosen)

    def is_clique(g, members):
        return all(g.has_edge(u, v) for u, v in combinations(members, 2))

    all_cliques = list(nx.find_cliques(G))

    # Property 1, 2, 3: each result is a valid maximal clique of valid nodes.
    for clique in all_cliques:
        assert len(set(clique)) == len(clique)  # no duplicate nodes
        for node in clique:
            assert node in G
        assert is_clique(G, clique)  # complete subgraph (self-loops irrelevant)
        cset = set(clique)
        # Maximality: no other node is adjacent to all members.
        for other in G.nodes():
            if other in cset:
                continue
            assert not all(G.has_edge(other, m) for m in cset)

    # Property 6: every node belongs to at least one maximal clique.
    covered = set()
    for clique in all_cliques:
        covered.update(clique)
    assert covered == set(G.nodes())

    # Now test the `nodes` parameter.
    mode = data.draw(st.sampled_from(["none", "valid_clique", "arbitrary"]),
                     label="nodes_mode")

    if mode == "none" or n == 0:
        result = list(nx.find_cliques(G, nodes=None))
        assert sorted(map(sorted, result)) == sorted(map(sorted, all_cliques))

    elif mode == "valid_clique":
        # Sample a non-empty subset of an existing maximal clique -> guaranteed clique.
        base = data.draw(st.sampled_from(all_cliques), label="base_clique")
        k = data.draw(st.integers(min_value=1, max_value=len(base)), label="subset_size")
        sub = data.draw(
            st.lists(st.sampled_from(base), min_size=k, max_size=k, unique=True),
            label="node_subset",
        )
        filtered = list(nx.find_cliques(G, nodes=sub))
        expected = [c for c in all_cliques if set(sub).issubset(set(c))]
        # Property 4: every filtered clique contains all of `nodes`,
        # and the filtered set matches the unfiltered cliques containing `nodes`.
        for clique in filtered:
            assert set(sub).issubset(set(clique))
        assert sorted(map(sorted, filtered)) == sorted(map(sorted, expected))

    else:  # arbitrary subset, may or may not be a clique
        sub = data.draw(
            st.lists(st.sampled_from(nodes), min_size=1, unique=True),
            label="arbitrary_subset",
        )
        if is_clique(G, sub):
            filtered = list(nx.find_cliques(G, nodes=sub))
            for clique in filtered:
                assert set(sub).issubset(set(clique))
        else:
            # Property 5: non-clique `nodes` raises ValueError.
            try:
                list(nx.find_cliques(G, nodes=sub))
                assert False, "Expected ValueError for non-clique nodes"
            except ValueError:
                pass
# End program