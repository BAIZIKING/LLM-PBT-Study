from hypothesis import given, strategies as st
import networkx as nx

# Summary: 
# - Generate a random directed graph with between 2-100 nodes
# - Pick 2 random nodes from the graph to use as node1 and node2
# - Optionally generate a default value to return if no LCA exists
# - Check that the result is either the default value (if provided), or one of the graph nodes
# - Check that the result is an ancestor of both node1 and node2, if a non-default LCA was found
@given(
    G=st.builds(lambda nodes, edges: nx.DiGraph(edges), 
                st.sets(st.integers(), min_size=2, max_size=100),
                st.lists(st.tuples(st.integers(), st.integers()), min_size=1)),
    node1=st.integers(), 
    node2=st.integers(),
    default=st.one_of(st.none(), st.integers(), st.text())
)
def test_lowest_common_ancestor(G, node1, node2, default):
    # Filter node1 and node2 to ensure they are actual nodes in the generated graph
    node1 = node1 if node1 in G else next(iter(G))
    node2 = node2 if node2 in G else next(iter(G))
    
    lca = nx.lowest_common_ancestor(G, node1, node2, default)
    
    if default is None:
        assert lca in G
    else:
        assert lca in G or lca == default
    
    if lca in G:
        assert nx.has_path(G, lca, node1) 
        assert nx.has_path(G, lca, node2)
# End program