from hypothesis import given, strategies as st
from itertools import combinations
import networkx


@st.composite
def graphs(draw, max_nodes=8):
    n = draw(st.integers(min_value=0, max_value=max_nodes))
    nodes = list(range(n))
    possible_edges = list(combinations(nodes, 2))
    edges = draw(
        st.lists(
            st.sampled_from(possible_edges) if possible_edges else st.nothing(),
            max_size=len(possible_edges),
            unique=True,
        )
    ) if possible_edges else []
    G = networkx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    return G


@given(g=graphs())
def test_networkx_find_cliques_no_duplicates(g):
    # Property 5: No duplicate maximal cliques are returned
    # (each, as a set of nodes, appears exactly once).
    seen = []
    for clique in networkx.find_cliques(g):
        clique_frozen = frozenset(clique)
        assert clique_frozen not in seen, (
            f"Duplicate clique found: {sorted(clique)}"
        )
        seen.append(clique_frozen)
# End program