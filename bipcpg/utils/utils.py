from typing import List, Iterable, Iterator, Optional

import networkx as nx
import numpy as np
import pandas as pd
from functools import reduce


def transform_3level_nested_dict_into_stacked_df(nested_dict: dict,
                                                 name: Optional = None) -> pd.DataFrame:
    """
    Transform a nested dictionary with three levels into a stacked :class:`pandas.DataFrame` with a 3 level multi-index
    and a single column. If ``name`` is passed, set the name of the column to ``name``.

    :param dict nested_dict: Three level nested dictionary to be transformed.
    :param str name: Name of single column found in returned :class:`pandas.DataFrame`
    :return: Stacked dataframe with multi-index level 0 corresponding to outermost nested_dict keys, multi-index level 1
        corresponding to nested_dict middle level keys and  multi-index level 2 corresponding to nested_dict innermost
        keys.
    :rtype: :class:`pandas.DataFrame`
    """
    reformed_dict = {(level1_key, level2_key, level3_key): [values]
                     for level1_key, level2_dict in nested_dict.items()
                     for level2_key, level3_dict in level2_dict.items()
                     for level3_key, values in level3_dict.items()}

    df = pd.DataFrame(reformed_dict).T
    df.index = df.index.set_names(['x', 'z', 'y'])
    if name is not None:
        df = df.rename(columns={0: name})
    return df


def transform_3level_nested_dict_into_df(
        nested_dict: dict) -> pd.DataFrame:  # TypedDict[str or int, TypedDict[str or int, TypedDict]]
    """
    Transform a nested dictionary with three levels into a stacked :class:`pandas.DataFrame` with a 2 level multi-index.

    :param dict nested_dict: Three level nested dictionary to be transformed.
    :return: :class:`pandas.DataFrame` with 2-level multi-index. multi-index level 0 corresponds to outermost
        ``nested_dict`` keys, multi-index level 1 corresponds to ``nested_dict`` middle level keys and columns
        correspond to ``nested_dict`` innermost keys.
    :rtype: :class:`pandas.DataFrame`
    """
    stacked_df = transform_3level_nested_dict_into_stacked_df(nested_dict)
    df = stacked_df.unstack(level=-1)
    df.columns = df.columns.droplevel(0)
    return df


def remove_reversed_duplicates(iterable: Iterable[Iterable]) -> tuple:
    """
    For an iterable object containing other iterables, yield items which do not have a reversed duplicate in a position
    with a smaller index.

    :param Iterable iterable: An iterable object containing other iterables.
    :return: Inner iterables which do not have a reversed duplicate in a position with a smaller index.
    :rtype: Iterator[Iterable]
    """

    # create a set for already seen elements
    seen = set()
    for item in iterable:
        # lists are mutable so we need tuples for the set-operations.
        tup = tuple(item)
        if tup not in seen:
            # if the tuple is not in the set append it in REVERSED order.
            seen.add(tup[::-1])

            yield item


def get_degrees_df(G: nx.DiGraph) -> pd.DataFrame:
    """
    Get a :class:`pandas.DataFrame` containing the degree, in-degree and out-degree information of the nodes in ``G``.

    :param `networkx.DiGraph` G: Directed network.
    :return: :class:`pandas.DataFrame` containing degree information.
    :rtype: :class:`pandas.DataFrame`

    """
    # get degree data
    list_node_degrees = sorted(G.degree, key=lambda x: x[1], reverse=True)
    list_node_out_degrees = sorted(G.out_degree, key=lambda x: x[1], reverse=True)
    list_node_in_degrees = sorted(G.in_degree, key=lambda x: x[1], reverse=True)

    # create dataframes
    df_node_degrees = pd.DataFrame(list_node_degrees, columns=["sector", "degree"])
    df_node_out_degrees = pd.DataFrame(list_node_out_degrees, columns=["sector", "out_degree"])
    df_node_in_degrees = pd.DataFrame(list_node_in_degrees, columns=["sector", "in_degree"])

    # merge dataframes
    list_degree_dfs = [df_node_degrees, df_node_out_degrees, df_node_in_degrees]
    degrees_df = reduce(lambda left, right: pd.merge(left, right, on=['sector'], how='outer'), list_degree_dfs)

    return degrees_df


def reshape_year_matrices_to_time_series_matrices(list_yearly_matrices: List[np.ndarray]) -> List[np.ndarray]:
    """
    For a list of :class:`numpy.ndarray` s, switch the first dimension (list entries) for the second dimension (axis 0)
    of matrices in the list.

    :param list list_yearly_matrices: list of 2-dimensional :class:`numpy.ndarray` s indexed over time. Each matrix has
        one set of variables of the bipartite dataset along axis 0 (rows) and the other set of variables in the
        bipartite dataset along axis 1 (columns).
    :return: list of 2-dimensional :class:`numpy.ndarray` indexed over the elements in the rows of the matrices in
        ``list_yearly_matrices``. Axis 0 (rows) of each matrix is now indexed over time, i.e. the dimension of the
        elements in ``list_yearly_matrices``.
    :rtype: :class:`list`

    :example:
        This can be used transform a list of matrices (one per year) into a list of time series matrices.
        Say we have a list ``my_list`` containing matrices (one per year) with the exports every country (rows) made for
        every product (columns). We can then transform this into a list of matrices (one per country) with time series
        observations along the rows and products along the columns.

    .. code-block:: python

        >>> my_list = [np.array([[1,2],[3,4]]),
        ...            np.array([[5,6],[7,8]]),
        ...            np.array([[9,10],[11,12]])]
        >>> my_list_transformed = transform_year_matrices_to_time_series_matrices(my_list)
        my_list_transformed
        [
        array([[ 1,  2],
               [ 5,  6],
               [ 9, 10]]),
        array([[ 3,  4],
               [ 7,  8],
               [11, 12]])
        ]

    """

    stacked = np.stack(list_yearly_matrices, axis=1)
    stacked_list = list(stacked)

    return stacked_list
