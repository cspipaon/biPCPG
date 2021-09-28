Code documentation
==================

PCPG class
----------

.. autoclass:: bipcpg.pcpg.PCPG
    :members:
    :undoc-members:
    :show-inheritance:


Correlations Functions
----------------------

.. automodule:: bipcpg.correlations
    :members: get_correlation_matrices_for_list_of_matrices, compute_corr_matrix, corr_pvalue_matrices
    :undoc-members:
    :show-inheritance:

Bootstrap functions
-------------------

.. automodule:: bipcpg.bootstrap
    :members: construct_corr_matrix_replicates_from_time_series_matrices, get_bootstrap_values
    :undoc-members:
    :show-inheritance:

Util functions
--------------

.. automodule:: bipcpg.utils.utils
    :members: transform_3level_nested_dict_into_stacked_df, transform_3level_nested_dict_into_df,
              remove_reversed_duplicates, get_degrees_df, reshape_year_matrices_to_time_series_matrices
    :undoc-members:
    :show-inheritance:

.. automodule:: bipcpg.utils.communities_utils
    :members: get_igraph_network_and_partition, communities_data
    :undoc-members:
    :show-inheritance: