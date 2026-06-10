from hypothesis import given, strategies as st
import networkx as nx

# Summary: 
# Generate a random graph by:
# 1. Generating a random number of nodes
# 2. Generate edges by repeatedly choosing 2 nodes at random 
#    and connecting them, allowing self-loops and parallel edges
# 3. Optionally generate a random subset of nodes to pass as 
#    the "nodes" parameter
#
# Properties to test:
# 1. Each returned clique should be a complete subgraph
# 2. Each clique should be maximal (not a subset of a larger clique) 
# 3. If "nodes" parameter is provided, each returned clique should
#    contain all nodes in "nodes"
# 4. If "nodes" is not a clique itself, should raise ValueError
# 5. Returned cliques should be unique (no duplicates)
@given(st.data())
def test_find_cliques(data):
    num_nodes = data.draw(st.integers(min_value=1, max_value=10))
    G = nx.Graph()
    G.add_nodes_from(range(num_nodes))
    
    num_edges = data.draw(st.integers(min_value=0, max_value=num_nodes*(num_nodes-1)//2))
    for _ in range(num_edges):
        u, v = data.draw(st.sampled_from(G.nodes), st.sampled_from(G.nodes))
        G.add_edge(u, v)

    subset_nodes = data.draw(st.booleans())
    nodes = data.draw(st.lists(st.sampled_from(G.nodes), min_size=1, max_size=num_nodes, 
                               unique=True)) if subset_nodes else None
    
    cliques = list(nx.find_cliques(G, nodes))

    for clique in cliques:
        # Each clique is a complete subgraph
        assert nx.is_clique(G, clique)
        # Cliques are maximal
        for node in set(G.nodes) - set(clique):
            assert not set(clique + [node]) <= set(G.nodes)
    
    if nodes:
        # All returned cliques contain specified nodes
        for clique in cliques:
            assert set(nodes) <= set(clique)
        # Raise ValueError if nodes isn't a clique  
        if not nx.is_clique(G, nodes):
            try:
                nx.find_cliques(G, nodes)
                assert False
            except ValueError:
                pass

    # No duplicate cliques  
    assert len(set(map(tuple, cliques))) == len(cliques)
# End program    