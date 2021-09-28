import numpy as np
import pandas as pd
from collections import Counter
from typing import Optional, Iterable

from .pcpg import PCPG
from .correlations import compute_corr_matrix


def construct_corr_matrix_replicates_from_time_series_matrices(array_of_matrices: np.array, num_replicates: int,
                                                               critical_value: Optional[float] = None):
    """
    Performs a bootstrap procedure on time series matrices to obtain correlation matrix replicates. If
    ``critical_value`` is not None, the correlation matrices are filtered using a statistical significance T-test.

    :param numpy.ndarray array_of_matrices: 3-dimensional ``numpy.ndarray`` with axis 0 representing elements of one of
        the sets in the bipartite system, axis 1 representing time series observations and axis 2 representing elements
        of the remaining set in the bipartite system.
    :param int num_replicates: Number of correlation matrix replicates to be constructed.
    :param float critical_value: If passed, boundary of the acceptance region of the T-test performed.
    :return: Array containing mean of correlation matrix replicates in each batch.
    :rtype: numpy.ndarray
    """

    # assert all(x.shape == array_of_matrices[0].shape for x in array_of_matrices)

    # find dimensions of dataset
    num_matrices_to_replicate = array_of_matrices.shape[0]
    num_rows_per_matrix = array_of_matrices[0].shape[0]
    num_cols_per_matrix = array_of_matrices[0].shape[1]

    # compute number of rows needed for each matrix in axis 0 to create replicates
    num_rows_needed = num_rows_per_matrix * num_replicates

    # create random indices to select random rows for each replicate
    selected_rows_indices = np.random.choice(a=num_rows_per_matrix, size=num_rows_needed)

    # select all rows needed for replicates
    # for each matrix in axis 0, we select num_rows_needed rows using the same indices: selected_rows_indices
    rows = np.take(array_of_matrices, selected_rows_indices, axis=1)

    # reshape so arrays along axis 1 contain replicates of the same matrix
    shape_gb_original_matrices = (num_matrices_to_replicate, num_replicates, num_rows_per_matrix, num_cols_per_matrix)
    replicates_gb_original_matrices = np.reshape(rows, shape_gb_original_matrices)

    # transpose so arrays along axis 1 contain replicates of the same batch
    ts_replicates_batches = np.transpose(replicates_gb_original_matrices, axes=[1, 0, 2, 3])

    # calculate a correlation matrix for each replicate time series matrix
    corr_replicates_gb_batch = np.array([np.array([compute_corr_matrix(ts_replicate, critical_value=critical_value)
                                                   for ts_replicate in ts_replicates_gb_batch])
                                         for ts_replicates_gb_batch in ts_replicates_batches])

    # calculate a mean correlation matrix for each batch of replicates
    means_of_batches = np.nanmean(corr_replicates_gb_batch, axis=1)

    return means_of_batches


def get_boostrap_values(timeseries_matrices: Iterable[np.ndarray], num_replicates: int = 1_000,
                        critical_value: Optional[float] = None) -> pd.DataFrame:
    """
    Compute bootstrap values for edges in a PCPG network. This function takes a dataset in the form of a list or
    numpy array of matrices with time series in its columns (see :ref:`dataset_info`) performs a bootstrap procedure
    that generates a total of ``num_replicates`` replicate PCPG matrices and finds the bootstrap value of each edge,
    i.e. the fraction of times the edge appears in these networks. If ``critical_value`` is not None, the replicate
    correlation matrices generated are filtered using a statistical significance T-test.

    :param list/numpy.ndarray timeseries_matrices: Iterable containing the dataset for which the PCPG network was
        generated. This should be a list containing matrices whose columns contain observations for one of the the two
        sets of variables in a bipartite dataset.
    :param int num_replicates: Number of replicates to generate in the bootstrap procedure.
    :param float critical_value: If passed, boundary of the acceptance region of the T-test performed.
    :return: pandas.DataFrame containing the bootstrap values of the *directed* edges in the PCPG network. Note that
        the source of an edge is its row index and the target of the edge is its column index.
    :rtype: :class:pandas.DataFrame
    """
    # compute correlation matrix replicates for list of time series matrices
    corr_matrix_replicates = construct_corr_matrix_replicates_from_time_series_matrices(
        array_of_matrices=timeseries_matrices, num_replicates=num_replicates, critical_value=critical_value)

    # for each correlation matrix replicate compute a PCPG network and save its edges
    edges_per_replicate = []
    for corr_matrix in corr_matrix_replicates:
        pcpg = PCPG(corr_matrix)
        pcpg.compute_avg_influence_matrix()
        edges = pcpg.find_edges()
        edges_per_replicate.append(edges)

    # count number of times each edge appears in the replicate PCPG networks
    flat_edges = [edge for replicate in edges_per_replicate for edge in replicate]
    edge_counts = Counter(flat_edges)

    # compute bootstrap values, i.e. fraction of times edges appear in the replicate PCPG networks
    edge_counts_df = pd.Series(edge_counts).unstack(level=-1)
    edge_bs_value_df = edge_counts_df / num_replicates

    # if edges have not appeared, assign bootstrap value of 0
    edge_bs_value_df = edge_bs_value_df.fillna(0)

    return edge_bs_value_df
