import numpy as np
import pandas as pd
from scipy.special import betainc

from typing import List, Tuple, Optional


def get_correlation_matrices_for_list_of_matrices(list_matrices: List[np.ndarray],
                                                  critical_value: Optional[float] = None) -> Tuple[
                                                                                    List[np.ndarray], List[np.ndarray]]:
    """
    Obtain a correlation matrix and p-value matrix for each matrix (containing variables along the columns and
    observations along the rows) in ``list_matrices``. If ``critical value`` is passed, each correlation matrix is
    filtered based on a statistical significance T-test where ``critical_value`` is the threshold value.

    :param list list_matrices: list of 2-dimensional ``numpy.ndarray`` s containing observations along axis 0 (rows)
        and variables along axis 1 (columns).
    :param float critical_value: Boundary of the acceptance region of the T-test performed.
    :return: tuple containing: (i) list of length len(list_time_series_matrices) containing correlation matrices
        displaying the correlation coefficients between the columns (axis 1) of each input matrix, and (ii) list of
        p-value matrices corresponding to each correlation matrix.
    :rtype: tuple
    """
    list_correlation_matrices = []
    for ts_matrix in list_matrices:
        corr_matrix, pvals_matrix = corr_pvalue_matrices(ts_matrix)

        if critical_value is not None:
            corr_matrix[pvals_matrix > critical_value] = np.nan

        list_correlation_matrices.append(corr_matrix)

    return list_correlation_matrices


def compute_corr_matrix(matrix: np.array or pd.DataFrame, critical_value: Optional[float] = None) -> np.ndarray:
    """
    Obtain a correlation matrix among the variables in a matrix. If ``critical value`` is passed, the correlation matrix
    is filtered based on a statistical significance T-test where ``critical_value`` is the threshold value.

    :param numpy.ndarray matrix: ``numpy.ndarray`` containing time series for the values of interest with
        observations along axis 0 (rows) and variables along axis 1 (columns).
    :param float critical_value: Boundary of the acceptance region of the T-test performed.
    :return: Correlation matrix displaying correlation coefficients between the columns (axis 1) of each input matrix.
    :rtype: numpy.ndarray
    """
    corr_matrix, pval_matrix = corr_pvalue_matrices(matrix)
    if critical_value is not None:
        corr_matrix[pval_matrix > critical_value] = np.nan

    return corr_matrix


def corr_pvalue_matrices(matrix: np.ndarray) -> tuple:
    """
    Obtain a correlation matrix and p-value matrix for a matrix containing variables and observations.

    :param numpy.ndarray matrix: 2-dimensional numpy.ndarray containing containing observations axis 0 and
        variables along axis 1.
    :return: tuple containing correlation matrix showing correlation coefficients between columns of input matrix
        and p-value matrix showing statistical significance of correlations.
    :rtype: tuple
    """
    matrix = matrix.T
    r = np.corrcoef(matrix)

    # upper triangular values of corr matrix
    rf = r[np.triu_indices(r.shape[0], k=1)]

    # num cols - 2
    df = matrix.shape[1] - 2

    # calculate p-values
    ts = rf * rf * (df / (1 - rf * rf))
    pf = betainc(0.5 * df, 0.5, df / (df + ts))

    # create p-value matrix
    p = np.zeros(shape=r.shape)
    p[np.triu_indices(p.shape[0], 1)] = pf
    p[np.tril_indices(p.shape[0], -1)] = p.T[np.tril_indices(p.shape[0], -1)]

    # round entries in arrays to avoid floating point errors, e.g, 0.999999999 instead of 1
    r, p = np.around(r, 4), np.around(p, 4)

    return np.transpose(r), np.transpose(p)
