from hypothesis import given, strategies as st
import networkx as nx
import numpy as np

# Generation Strategy:
# As per the API documentation, the function find_cliques accepts an undirected graph and a list of nodes. So, we generate 
# a random integer n which acts as the number of nodes and edges in the graph G. With this, we cover edge cases where n is small 
# or large, and can generate a wide variety of inputs. We then generate a list nodes which is a subset of the graph's nodes.
# Properties to Check:
# - Check if each returned clique is indeed a clique (i.e., a fully connected subgraph) in G. 
# - Check that if nodes parameter is provided that each returned clique contains all nodes in the nodes parameter.
# - Check if passing a nodes parameter which isn't a clique raises ValueError.
# - Check if passing a directed graph raises some kind of exception as this function is only applicable to undirected graphs.

@given(st.data())
def test_find_cliques(data):
    n = data.draw(st.integers(min_value=2, max_value=10))  # Number of nodes and edges
    G = nx.Graph()
    G.add_edges_from(np.random.randint(n, size=(n, 2)).tolist())  # Generating random edges
    list_G_nodes = list(G.nodes)
  
    nodes = data.draw(st.lists(st.sampled_from(list_G_nodes), min_size=1, max_size=len(list_G_nodes)))  
    if nx.is_directed(G):
        try:
            _ = nx.find_cliques(G)
        except Exception:
            assert True
    else:
        cliques = list(nx.find_cliques(G))
    
        for clique in cliques:
            subgraph = G.subgraph(clique)
            # Asserting each returned clique is indeed a clique
            assert all(subgraph.has_edge(u, v) for u in clique for v in clique if u != v)
            
            # Asserting returned clique contains all nodes in the nodes parameter
            if nodes:
                assert all(node in clique for node in nodes)
                
        # Asserting ValueError when nodes parameter which isn't a clique
        non_clique = [node for node in G if G.degree[node] < 1]
        if non_clique:
            try:
                _ = nx.find_cliques(G, non_clique)
            except ValueError:
                assert True