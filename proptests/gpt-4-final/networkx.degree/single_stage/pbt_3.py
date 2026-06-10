from hypothesis import given, strategies as st
import networkx as nx

@given(st.data())
def test_networkx_degree(data):
    # Generate a range of values for nodes
    nodes = data.draw(st.lists(st.integers(min_value=0, max_value=100), min_size=2, max_size=10, unique=True))
    
    # Generate random values for nbunch
    nbunch = data.draw(st.lists(st.integers(min_value=0, max_value=100), min_size=1, unique=True)) 

    G = nx.Graph()
    # Add nodes to graph
    G.add_nodes_from(nodes)

    # Generate random weights
    weight = data.draw(st.text(min_size=1, max_size=10))

    degree_all = nx.degree(G, weight=weight) 

    try:
      degree_nbunch = nx.degree(G, nbunch, weight=weight)
    except:
      degree_nbunch = None

    assert isinstance(degree_all, nx.classes.reportviews.DegreeView)
    if degree_nbunch: 
      assert len(degree_nbunch) <= len(degree_all)