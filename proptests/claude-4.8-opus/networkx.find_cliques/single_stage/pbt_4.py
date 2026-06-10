from hypothesis import given, strategies as st
import networkx as nx
from itertools import combinations

# Summary: Generate a random undirected graph by choosing a node count and a
# random subset of possible edges (optionally including self-loops). Then use
# st.data() to optionally sample a subset of actual nodes to pass as `nodes`.
# Verify that each output is a maximal clique consisting of valid graph nodes,
# that `nodes` is contained in every clique when it's a valid clique, and that
# a ValueError is raised when `nodes` is not itself a clique.
@given(st.data())
def test_networkx_find_cliques(data):
    n = data.draw(st.integers(min_value=0, max_value=8), label="num_nodes")
    nodes_list = list(range(n))

    # Possible undirected edges (including potential self-loops to test ignoring)
    possible_edges = list(combinations(nodes_list, 2)) + [(i, i) for i in nodes_list]
    if possible_edges:
        chosen_edges = data.draw(
            st.lists(st.sampled_from(possible_edges), unique=True),
            label="edges",
        )
    else:
        chosen_edges = []

    G = nx.Graph()
    G.add_nodes_from(nodes_list)
    G.add_edges_from(chosen_edges)

    # Helper: are all distinct pairs in `clique` adjacent (ignoring self-loops)?
    def is_clique(clique):
        for u, v in combinations(set(clique), 2):
            if not G.has_edge(u, v):
                return False
        return True

    # Optionally choose a `nodes` argument from actual graph nodes.
    use_nodes = data.draw(st.booleans(), label="use_nodes")
    selected_nodes = None
    if use_nodes and n > 0:
        selected_nodes = data.draw(
            st.lists(st.sampled_from(nodes_list), unique=True),
            label="selected_nodes",
        )

    # Determine if selected_nodes forms a clique (None -> treat as valid/no constraint).
    nodes_is_clique = selected_nodes is None or is_clique(selected_nodes)

    if selected_nodes is not None and not nodes_is_clique:
        # Property 4: non-clique `nodes` must raise ValueError.
        try:
            list(nx.find_cliques(G, nodes=selected_nodes))
            assert False, "Expected ValueError for non-clique nodes argument"
        except ValueError:
            return  # Correct behavior; nothing more to check.

    cliques = list(nx.find_cliques(G, nodes=selected_nodes))

    all_nodes = set(G.nodes())
    for clique in cliques:
        clique_set = set(clique)

        # Property 2: every node in the clique is a node of G.
        assert clique_set <= all_nodes

        # Property 1a: it is a clique (ignoring self-loops).
        assert is_clique(clique)

        # Property 1b: it is maximal -- no external node is adjacent to all members.
        for other in all_nodes - clique_set:
            adjacent_to_all = all(G.has_edge(other, c) for c in clique_set)
            assert not adjacent_to_all, (
                f"Clique {clique} is not maximal; node {other} could extend it"
            )

        # Property 3: when `nodes` is a valid clique, it is contained in each result.
        if selected_nodes is not None:
            assert set(selected_nodes) <= clique_set
# End program