from collections import Counter
import igraph as ig
import leidenalg as la
import networkx as nx


def get_igraph_network_and_partition(G: nx.Graph, **la_kwds) -> tuple:
    """
    Obtain an ``igraph`` graph and a partition from a ``networkx`` graph.
    :param networkx.Graph G: `networkx` graph to be converted into `igraph` graph.
    :param la_kwds: keyword arguments passed on to ``leidenalg.find_partition()``.
    :return:
        - partition :class:`leidenalg.VertexPartition` - Graph partition.
        - H :class:`igraph.Graph` - ``igraph`` graph object.
    """
    # convert networkx graph to igraph graph
    H = ig.Graph.from_networkx(G)

    # find partition of communities using modularity algorithm
    partition = la.find_partition(H, la.ModularityVertexPartition, **la_kwds)

    return H, partition


def communities_data(G: nx.Graph, **la_kwds) -> tuple:
    """
    Perform a community detection procedure on graph ``G`` and return relevant results for plotting.

    :param :class:nx.Graph G: ``networkx`` graph on which to perform community detection.
    :param la_kwds: keyword arguments passed on to :py:func:`leidenalg.find_partition`.
    :return:
        - G_igraph :class:`igraph.Graph` - `igraph` graph object equivalent to ``G``.
        - partition :class:`leidenalg.VertexPartition` - Graph partition.
        - tup_nodes_num_nodes :py:class:tuple - ``tuple`` containing list of nodes sorted by community and list of
        number of nodes per community
    :rtype: tuple
    """
    G_igraph, partition = get_igraph_network_and_partition(G, **la_kwds)

    # create dictionary with networkx node name as key and community id as value
    node_names_nx = G_igraph.vs['_nx_name']
    node_ids_ig = G_igraph.vs.indices
    node_memberships = [partition.membership[node] for node in node_ids_ig]
    communities_dict = dict(zip(node_names_nx, node_memberships))

    # find number of nodes in each community
    nodes_in_each_comm_dict = Counter(node_memberships)
    num_nodes_in_each_comm = [value for key, value in sorted(nodes_in_each_comm_dict.items(), reverse=False)]

    # get list of nodes sorted by their respective community
    nodes_sorted_by_community = sorted(communities_dict, key=communities_dict.get)

    # create tuple containing lists of sorted nodes and number of nodes per community
    tup_nodes_num_nodes = tuple([nodes_sorted_by_community, num_nodes_in_each_comm])

    return G_igraph, partition, tup_nodes_num_nodes
