from hypothesis import given, strategies as st
import networkx as nx
from itertools import combinations

# Summary: Generate random undirected graphs from a sampled set of integer nodes
# and a sampled subset of possible edges (optionally adding self-loops). The
# `nodes` argument is chosen via st.data() to cover None, a guaranteed-clique
# subset, and a possibly-non-clique subset. We check that returned cliques are
# valid maximal cliques, that self-loops are ignored, that `nodes` containment
# holds, and that a non-clique `nodes` raises ValueError.
@given(st.data())
def test_networkx_find_cliques(data):
    # --- Build the graph ---
    n = data.draw(st.integers(min_value=0, max_value=8), label="num_nodes")
    nodes = list(range(n))
    possible_edges = list(combinations(nodes, 2))
    chosen_edges = data.draw(
        st.lists(st.sampled_from(possible_edges), unique=True)
        if possible_edges else st.just([]),
        label="edges",
    )
    add_self_loops = data.draw(st.booleans(), label="add_self_loops")

    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(chosen_edges)
    if add_self_loops and nodes:
        loop_nodes = data.draw(
            st.lists(st.sampled_from(nodes), unique=True), label="self_loop_nodes"
        )
        G.add_edges_from((u, u) for u in loop_nodes)

    adj = {u: set(G[u]) - {u} for u in G}  # adjacency without self-loops

    # --- Property: cliques returned with nodes=None are valid & maximal ---
    all_cliques = list(nx.find_cliques(G))
    for clique in all_cliques:
        cset = set(clique)
        # Valid clique: every distinct pair is adjacent.
        for a, b in combinations(cset, 2):
            assert b in adj[a], f"{clique} is not a clique: {a},{b} not adjacent"
        # Maximal: no outside node adjacent to all clique members.
        for v in G:
            if v not in cset:
                assert not cset.issubset(adj[v]), f"{clique} is not maximal (extend by {v})"

    # --- Property: self-loops are ignored ---
    G_no_loops = nx.Graph()
    G_no_loops.add_nodes_from(nodes)
    G_no_loops.add_edges_from((u, v) for u, v in G.edges() if u != v)
    cliques_clean = {frozenset(c) for c in nx.find_cliques(G_no_loops)}
    cliques_orig = {frozenset(c) for c in all_cliques}
    assert cliques_clean == cliques_orig, "self-loops changed the resulting cliques"

    # --- Choose a `nodes` argument and test containment / ValueError ---
    if n > 0:
        mode = data.draw(st.sampled_from(["none", "clique", "arbitrary"]), label="mode")
    else:
        mode = "none"

    if mode == "none":
        return

    if mode == "clique":
        # Pick a guaranteed clique: a single node, or both endpoints of an edge.
        real_edges = [(u, v) for u, v in chosen_edges]
        if real_edges and data.draw(st.booleans(), label="use_edge"):
            u, v = data.draw(st.sampled_from(real_edges), label="edge")
            query = [u, v]
        else:
            query = [data.draw(st.sampled_from(nodes), label="single")]

        result = list(nx.find_cliques(G, nodes=query))
        qset = set(query)
        for clique in result:
            assert qset.issubset(set(clique)), (
                f"clique {clique} does not contain query nodes {query}"
            )

    else:  # mode == "arbitrary"
        query = data.draw(
            st.lists(st.sampled_from(nodes), min_size=1, unique=True),
            label="arbitrary_query",
        )
        qset = set(query)
        # Determine whether query is actually a clique (ignoring self-loops).
        is_clique = all(b in adj[a] for a, b in combinations(qset, 2))
        if is_clique:
            result = list(nx.find_cliques(G, nodes=query))
            for clique in result:
                assert qset.issubset(set(clique)), (
                    f"clique {clique} does not contain query nodes {query}"
                )
        else:
            try:
                list(nx.find_cliques(G, nodes=query))
                assert False, "expected ValueError for non-clique nodes"
            except ValueError:
                pass
# End program