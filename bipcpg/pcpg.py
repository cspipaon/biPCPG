from typing import List, Optional
from copy import deepcopy

import warnings
import pandas as pd
import numpy as np
import networkx as nx

from utils.utils import remove_reversed_duplicates, transform_3level_nested_dict_into_df, \
    transform_3level_nested_dict_into_stacked_df


class PCPG:
    """
    Class to obtain a Partial Correlation Planar Graph (PCPG) network from a correlation matrix. [1]

    :param :class:pandas.DataFrame/:class:numpy.ndarray corr_matrix: Correlation matrix displaying correlations
        among variables in the system.
    :param list variable_names: Names of the variables in the system. The order of this list should coincide with
        the order of rows and columns in ``corr_matrix``.

    This class includes methods to perform the necessary computations and obtain a :class:~`networkx.Graph` network
    object. The PCPG algorithm consists in the following steps:

        1. find the *Average influence* (AI) between every *ordered* pair of variables in the system (in this
        case those in the correlation matrix),
        2. list the AIs in order from largest to smallest,
        3. iterate through the list and add a *directed* edge corresponding to the pair of variables of the
        AI value in that position **if and only if** (i) the reversed edge is not already in the network and (ii)
        the network's planarity is not broken by adding the edge.

    Attributes
    ----------
    :attr:`avg_influence_matrix`: Matrix containing average influence values between pairs of variables.
    :attr:`avg_influence_df`: ``pandas.DataFrame`` containing average influence values between pairs of variables.
    :attr:`influence_df`: ``pandas.DataFrame`` containing influence values between pairs of variables.
    :attr:`partial_corr_df`: multi-index ``pandas.DataFrame`` partial correlation values between triple of
    variables.
    :attr:`network`: the PCPG network (a ``networkx.DiGraph`` directed graph object).

    Methods
    -------
    :func:`compute_average_influence_matrix`: Performs step 1 of the PCPG algorithm.
    :func:`compute_influence_avg_influence_partial_corr_dfs`: Perform step 1 of PCPG algorithm saving influence,
        average influence and partial correlation data.
    :func:`create_network`: Performs steps 2 and 3 of the PCPG algorithm.
    :func:`find_edges: Compute edges in the PCPG network using :attr:`avg_influence_matrix`:
    :func:`add_edge_attribute`: Add data to the edges in the PCPG network.
    :func:`add_node_attribute`: Add data to the nodes in the PCPG network.
    :func:`compute_assortativity`: Compute assortativity of network nodes based on a node attribute.

    References
    ----------
    .. [1]_ Kenett DY, Tumminello M, Madi A, Gur-Gershgoren G, Mantegna RN, Ben-Jacob E (2010) Dominating Clasp of the
           Financial Sector Revealed by Partial Correlation Analysis of the Stock Market. PLoS ONE 5(12): e15032.
           <https://doi.org/10.1371/journal.pone.0015032>

    """
    def __init__(self,
                 corr_matrix: pd.DataFrame or np.ndarray,
                 variable_names: Optional[List] = None):

        if isinstance(corr_matrix, pd.DataFrame):
            assert corr_matrix.index.equals(
                corr_matrix.columns), 'corr_matrix index and columns are not labeled the same'

            self.dict_var_names = {i: corr_matrix.index[i] for i in range(len(corr_matrix.index))}
            if variable_names is not None:
                warnings.warn(
                    "WARNING: If corr_matrix is a pd.DataFrame, var_names is disregarded and index/columns of "
                    "corr_matrix are used as variable names.")
            self.corr_matrix = corr_matrix.values
            self.nodes = list(corr_matrix.index)

        elif isinstance(corr_matrix, np.ndarray):
            assert corr_matrix.shape[0] == corr_matrix.shape[1], 'corr_matrix is not square'

            if variable_names is not None:
                self.dict_var_names = {i: variable_names[i] for i in range(corr_matrix.shape[0])}
            else:
                self.dict_var_names = {i: i for i in range(corr_matrix.shape[0])}
                variable_names = [i for i in range(corr_matrix.shape[0])]

            self.nodes = variable_names
            self.corr_matrix = corr_matrix

        self.avg_influence_matrix = None  # avg influence direction is row -> col
        self.avg_influence_df = None  # avg influence direction is row -> col
        self.influence_df = None  # multi-index levels are x, z variables; columns are y variables
        self.partial_corr_df = None  # multi-index levels are x, z variables; columns are y variables
        self.network = None

    def compute_avg_influence_matrix(self):
        """
        Compute average influences between every pair of variables in the system and put these in
        ``self.avg_influence_matrix``.

        :return: None

        """
        variables = [i for i in range(len(self.nodes))]
        avg_influence_matrix = np.zeros(self.corr_matrix.shape)

        for x in variables:
            # remove x from list of y variables
            y_vars = deepcopy(variables)
            y_vars.remove(x)

            for z in variables:
                # list to save computed values
                influence_list = []

                for y in y_vars:
                    # find correlations between x, y, z
                    corr_xy, corr_xz, corr_yz = self.corr_matrix[x, y], self.corr_matrix[x, z], self.corr_matrix[y, z]

                    # compute influence of z on x and y
                    influence_xy_z = corr_xy - ((corr_xy - corr_xz * corr_yz) / np.sqrt(
                        (1 - corr_xz ** 2) * (1 - corr_yz ** 2)))
                    influence_list.append(influence_xy_z)

                avg_influence_matrix[x, z] = np.nanmean(influence_list)

        # self.avg_influence_df = pd.DataFrame(avg_influence_matrix.T, index=self.nodes, columns=self.nodes)
        self.avg_influence_matrix = avg_influence_matrix.T

    def compute_influence_avg_influence_partial_corr_dfs(self):
        """
        Compute partial correlations, influences and average influences between all variables in the system and put
        these in :attr:`partial_corr_df`, :attr:`influence_df` and :attr:`avg_influence_df` respectively.

        :return: None

        """
        avg_influence_dict = {}
        partial_corr_dict = {}
        influence_dict = {}

        variables = [i for i in range(len(self.nodes))]

        for x in variables:
            avg_influence_xz_dict = {}
            partial_corr_xz_dict = {}
            influence_xz_dict = {}

            # remove x from list of y variables
            y_vars = deepcopy(variables)
            y_vars.remove(x)

            for z in variables:
                # list to save computed values
                partial_corr_xy_z_dict = {}
                influence_xy_z_dict = {}
                influence_list = []

                for y in y_vars:
                    # find correlations between x, y, z
                    corr_xy, corr_xz, corr_yz = self.corr_matrix[x, y], self.corr_matrix[x, z], self.corr_matrix[y, z]

                    # compute partial correlation
                    partial_corr_xy_z = (corr_xy - corr_xz * corr_yz) / np.sqrt((1 - corr_xz ** 2) * (1 - corr_yz ** 2))
                    partial_corr_xy_z_dict[y] = partial_corr_xy_z

                    # compute influence of z on x and y
                    influence_xy_z = corr_xy - partial_corr_xy_z
                    influence_xy_z_dict[y] = influence_xy_z
                    influence_list.append(influence_xy_z)

                avg_influence_xz_dict[z] = np.nanmean(influence_list)
                partial_corr_xz_dict[z] = partial_corr_xy_z_dict
                influence_xz_dict[z] = influence_xy_z_dict

            avg_influence_dict[x] = avg_influence_xz_dict
            partial_corr_dict[x] = partial_corr_xz_dict
            influence_dict[x] = influence_xz_dict

        self.avg_influence_df = pd.DataFrame.from_dict(avg_influence_dict, orient='columns')
        self.partial_corr_df = transform_3level_nested_dict_into_df(partial_corr_dict)
        self.influence_df = transform_3level_nested_dict_into_stacked_df(influence_dict)

        self.avg_influence_df = self.avg_influence_df.rename(index=self.dict_var_names, columns=self.dict_var_names)
        self.partial_corr_df = self.partial_corr_df.rename(index=self.dict_var_names, columns=self.dict_var_names)
        self.influence_df = self.influence_df.rename(index=self.dict_var_names, columns=self.dict_var_names)

    def create_network(self):
        """
        Create PCPG a :class:nx.DiGraph network with :attr:`nodes`: and edges found following the PCPG algorithm.

        :return: None

        """
        # create a graph with nodes from variable names and no edges
        network = nx.DiGraph()
        network.add_nodes_from(self.nodes)

        edges = self.find_edges()
        edges = [(self.dict_var_names[source], self.dict_var_names[target]) for source, target in edges]
        network.add_edges_from(edges)

        # check number of edges is 3*(num_nodes-2)
        num_nodes = len(self.nodes)
        assert len(edges) == 3 * (num_nodes - 2), \
            f'Number of edges should be {3 * (num_nodes - 2)} but {len(edges)} were found'

        self.network = network

    def find_edges(self) -> list:
        """
        Compute the edges in the PCPG network using the average influences in :attr:`avg_influence_matrix`.

        :return: List of edges in the PCPG network
        :rtype: list

        """
        # get potential edges list sorted in descending average influence order
        avg_influence_df = pd.DataFrame(self.avg_influence_matrix)
        avg_influence_values = avg_influence_df.stack().dropna().sort_values(ascending=False)

        _network = nx.DiGraph()
        _network.add_nodes_from(self.nodes)
        num_nodes = len(self.nodes)

        # remove smallest among influences: x->z and z->x
        avg_influences_crop = list(remove_reversed_duplicates(avg_influence_values.index))

        edges_kept = []
        for i in range(len(avg_influences_crop)):
            source_node = avg_influences_crop[i][0]
            target_node = avg_influences_crop[i][1]

            # add_edge
            _network.add_edge(source_node, target_node)

            # if graph is still planar, keep edge, otherwise remove from _network
            if nx.check_planarity(_network)[0]:
                edges_kept.append((source_node, target_node))

                if len(edges_kept) >= 3 * (num_nodes - 2):
                    break
            else:
                _network.remove_edge(source_node, target_node)

        return edges_kept

    def add_edge_attribute(self, attr_data: dict or pd.DataFrame, attr_name: str):
        """
        Adds data for single attribute to edges in :attr:`network`.

        :param dict/:class:pd.DataFrame attr_data: pd.DataFrame or dictionary containing edge attribute values.
        :param str attr_name: Name of attribute to be added to edges.

        .. :note:
            If attr_data is a :class:pd.DataFrame, rows should indicate the tail of the edge (i.e. the origin node) and
            columns should indicate the head of the edge (i.e. the target node).
            If attr_data is a dictionary, keys should be tuples of the form (origin_node, target_node).

        """
        assert isinstance(self.network, nx.DiGraph), \
            'network object has not been created. The "create_network()" method must be called before this method'

        if isinstance(attr_data, dict):
            assert all([isinstance(type(k), tuple) for k in attr_data.keys()]), \
                'if edge_attribute_values is of type dict, keys should be tuples of the form (origin_node, target_node)'
        elif isinstance(attr_data, pd.DataFrame):
            attr_data = {(row, col): attr_data.at[row, col] for row in attr_data.index for col in attr_data.columns}

        nx.set_edge_attributes(self.network, values=attr_data, name=attr_name)

    def add_node_attribute(self, attr_data: dict or pd.DataFrame, attr_name: str):
        """
        Adds node attribute data to nodes in :attr:`network`.

        :param dict/:class:pd.DataFrame attr_data: :class:pd.Series or dictionary containing node attribute values.
        :param str attr_name: Name of attribute added.

        .. :note:
            If ``edge_attribute_values`` is a :class:pandas.Series, its index should contain the node and its values the
            attribute data.
            If ``edge_attribute_values`` is a dictionary, keys should be nodes and values should be attribute data.

        """
        assert isinstance(self.network, nx.DiGraph), \
            'Network object has not been created. The "create_network()" method must be called before this method'

        if isinstance(attr_data, pd.Series):
            attr_data = {node: attr_data.at[node] for node in attr_data.index}

        nx.set_node_attributes(self.network, values=attr_data, name=attr_name)

    def compute_assortativity(self, node_attribute: str, attr_type: str) -> float:
        """
        Compute node assortativity based on ``node_attribute`` of nodes.

        :param str node_attribute: Name of node attribute by which to compute assortativity.
        :param str attr_type: Either "qual" or "quant". Indicates if attribute data is either a qualitative
            characteristic or a quantitative characteristic.
        :return: Value of calculated assortativity.
        :rtype: float

        """
        if attr_type == 'qual':
            assortativity = nx.attribute_assortativity_coefficient(self.network, node_attribute)
        elif attr_type == 'quant':
            assortativity = nx.numeric_assortativity_coefficient(self.network, node_attribute)
        else:
            raise ValueError('"attr_type" keyword argument must be either "qual" or "quant".')

        return assortativity
