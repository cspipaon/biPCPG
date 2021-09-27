.. _tutorial:

Tutorial
========

The :mod:`bi_pcpg` package facilitates the computation of a Partial Correlation Planar Graph (PCPG) network for datasets
with a bipartite structure, as well as the preparation of the data for this purpose and a bootstrapping procedure to
assess the reliability of the edges in the network. Below we give an example of how to apply these methods to
a toy dataset consisting of countries and the products they export with the aim of obtaining a PCPG network with
products as nodes.

.. _dataset_info:

Dataset structure
-----------------
Consider a bipartite dataset containing the quantity (in millions of dollars) of a set products exported by a set of
countries. In this toy example, assume we have data for 4 countries, 4 products over a 5 year span with one data point
per year. Lets denote the countries :math:`c_1` to :math:`c_4`, the products :math:`p_1` to :math:`p_4`
and the years :math:`y_1` to :math:`y_5`. Furthermore, denote the quantity of exports a given country does of a given
product in a given year by :math:`e_{cp}^y`.

This sort of dataset is usually distributed as a collection of tables indexed over time containing the data for that
given year. Following our example, we would have the following tables or matrices.

For the first year :math:`y_1`:

.. csv-table::

               , :math:`p_1`, :math:`p_2`, :math:`p_3`, :math:`p_4`
    :math:`c_1`, :math:`e_{c_1 p_1}^{y_1}`, :math:`e_{c_1 p_2}^{y_1}`, :math:`e_{c_1 p_3}^{y_1}`, :math:`e_{c_1 p_4}^{y_1}`
    :math:`c_2`, :math:`e_{c_2 p_1}^{y_1}`, :math:`e_{c_2 p_2}^{y_1}`, :math:`e_{c_2 p_3}^{y_1}`, :math:`e_{c_2 p_4}^{y_1}`
    :math:`c_3`, :math:`e_{c_3 p_1}^{y_1}`, :math:`e_{c_3 p_2}^{y_1}`, :math:`e_{c_3 p_3}^{y_1}`, :math:`e_{c_3 p_4}^{y_1}`
    :math:`c_4`, :math:`e_{c_4 p_1}^{y_1}`, :math:`e_{c_4 p_2}^{y_1}`, :math:`e_{c_4 p_3}^{y_1}`, :math:`e_{c_4 p_4}^{y_1}`

for the second year :math:`y_2`:

.. csv-table::

               , :math:`p_1`, :math:`p_2`, :math:`p_3`, :math:`p_4`
    :math:`c_1`, :math:`e_{c_1 p_1}^{y_2}`, :math:`e_{c_1 p_2}^{y_2}`, :math:`e_{c_1 p_3}^{y_2}`, :math:`e_{c_1 p_4}^{y_2}`
    :math:`c_2`, :math:`e_{c_2 p_1}^{y_2}`, :math:`e_{c_2 p_2}^{y_2}`, :math:`e_{c_2 p_3}^{y_2}`, :math:`e_{c_2 p_4}^{y_2}`
    :math:`c_3`, :math:`e_{c_3 p_1}^{y_2}`, :math:`e_{c_3 p_2}^{y_2}`, :math:`e_{c_3 p_3}^{y_2}`, :math:`e_{c_3 p_4}^{y_2}`
    :math:`c_4`, :math:`e_{c_4 p_1}^{y_2}`, :math:`e_{c_4 p_2}^{y_2}`, :math:`e_{c_4 p_3}^{y_2}`, :math:`e_{c_4 p_4}^{y_2}`

and similarly for years :math:`y_3`, :math:`y_4` and :math:`y_5`.

In order to use such a dataset with the :mod:`bi_pcpg` package, we have to reshape the data such that, instead of having
a matrix per time index, we have a matrix per element of one of the two sets of variables. These matrices
should have rows representing time indices and columns representing the complementary set of variables. In our
example, instead of a matrix per year, we could reshape the dataset into either a matrix per country or a matrix per
product. If we shape the data such that we have one matrix per country and apply the Bipartite PCPG (biPCPG) algorithm,
we would obtain a network whose nodes are products, and vice versa.

Given we want to obtain a network of products, we need to reshape our data such that we have four matrices, one per
country, containing the export time series for each products as columns. Using the notation introduced above, these
matrices have the following structure:

The matrix for country :math:`c_1`:

.. csv-table::

               , :math:`p_1`, :math:`p_2`, :math:`p_3`, :math:`p_4`
    :math:`y_1`, :math:`e_{c_1 p_1}^{y_1}`, :math:`e_{c_1 p_2}^{y_1}`, :math:`e_{c_1 p_3}^{y_1}`, :math:`e_{c_1 p_4}^{y_1}`
    :math:`y_2`, :math:`e_{c_1 p_1}^{y_2}`, :math:`e_{c_1 p_2}^{y_2}`, :math:`e_{c_1 p_3}^{y_2}`, :math:`e_{c_1 p_4}^{y_2}`
    :math:`y_3`, :math:`e_{c_1 p_1}^{y_3}`, :math:`e_{c_1 p_2}^{y_3}`, :math:`e_{c_1 p_3}^{y_3}`, :math:`e_{c_1 p_4}^{y_3}`
    :math:`y_4`, :math:`e_{c_1 p_1}^{y_4}`, :math:`e_{c_1 p_2}^{y_4}`, :math:`e_{c_1 p_3}^{y_4}`, :math:`e_{c_1 p_4}^{y_4}`
    :math:`y_5`, :math:`e_{c_1 p_1}^{y_5}`, :math:`e_{c_1 p_2}^{y_5}`, :math:`e_{c_1 p_3}^{y_5}`, :math:`e_{c_1 p_4}^{y_5}`

the matrix for country :math:`c_2`:

.. csv-table::

               , :math:`p_1`, :math:`p_2`, :math:`p_3`, :math:`p_4`
    :math:`y_1`, :math:`e_{c_2 p_1}^{y_1}`, :math:`e_{c_2 p_2}^{y_1}`, :math:`e_{c_2 p_3}^{y_1}`, :math:`e_{c_2 p_4}^{y_1}`
    :math:`y_2`, :math:`e_{c_2 p_1}^{y_2}`, :math:`e_{c_2 p_2}^{y_2}`, :math:`e_{c_2 p_3}^{y_2}`, :math:`e_{c_2 p_4}^{y_2}`
    :math:`y_3`, :math:`e_{c_2 p_1}^{y_3}`, :math:`e_{c_2 p_2}^{y_3}`, :math:`e_{c_2 p_3}^{y_3}`, :math:`e_{c_2 p_4}^{y_3}`
    :math:`y_4`, :math:`e_{c_2 p_1}^{y_4}`, :math:`e_{c_2 p_2}^{y_4}`, :math:`e_{c_2 p_3}^{y_4}`, :math:`e_{c_2 p_4}^{y_4}`
    :math:`y_5`, :math:`e_{c_2 p_1}^{y_5}`, :math:`e_{c_2 p_2}^{y_5}`, :math:`e_{c_2 p_3}^{y_5}`, :math:`e_{c_2 p_4}^{y_5}`

and similarly for countries :math:`c_3` and :math:`c_4`.

Now lets see how the above translates into code. Take the following ``dataset``, with a matrix **per year** as an
example:

.. code-block:: python

    >>> import numpy as np
        dataset = [np.array([[1.2, 3., 1., 5.4],                 # y_1 data
                             [10.2, 8.8, 11.7, 15.2],            #
                             [101.7, 99.7, 104.2, 103.8],        #
                             [1001.9, 1002.7, 1000.7, 1004.7]]), #
                   np.array([[0.1, 5.2, 4.5, 4.2],               ## y_2 data
                             [9.1, 12.2, 13.4, 11.7],            ##
                             [105.5, 102.9, 106.5, 101.9],       ##
                             [1004.4, 999.4, 1001.8, 1005.2]]),  ##
                   np.array([[1.3, 2.3, 1., 5.9],                ### y_3 data
                             [15.4, 14., 12.6, 15.8],            ###
                             [98.9, 103.2, 100.5, 104.2],        ###
                             [1000.9, 1003.8, 1002.6, 1006.6]]), ###
                   np.array([[0.9, 4., 4.9, 0.6],                #### y_4 data
                             [11.4, 12.4, 11.7, 14.7],           ####
                             [98.4, 103.4, 104.3, 104.9],        ####
                             [1006.3, 1003., 1003.4, 1002.8]]),  ####
                   np.array([[2., 0.5, 5.9, 3.1],                ##### y_5 data
                             [11.7, 16.4, 15.7, 14.9],           #####
                             [104.2, 102.3, 105., 104.4],        #####
                             [999.6, 1003.3, 1005.3, 1003.7]])]  #####

Recall that each array in the list ``dataset`` represents the exports (in millions of dollars) for a given year, where
rows represent countries and columns represent products. We would therefore have:

* :math:`e_{c_1 p_1}^{y_1}=\$1.2 \text{M}` = ``dataset[0][0][0] * 10**6``
* :math:`e_{c_3 p_2}^{y_2}=\$102.9 \text{M}` = ``dataset[1][2][1] * 10**6``
* :math:`e_{c_2 p_1}^{y_4}=\$11.4 \text{M}` = ``dataset[3][1][0] * 10**6``

Now let's see how we can convert the ``dataset`` with a matrix per year into a ``timeseries_dataset`` with one matrix
per country. In order to do the necessary reshaping we simply do:

>>> from bi_pcpg.utils.utils import reshape_year_matrices_to_time_series_matrices
    timeseries_dataset = reshape_year_matrices_to_time_series_matrices(dataset)

Note that :func:`~bi_pcpg.utils.utils.reshape_year_matrices_to_time_series_matrices` converts this into a list of
**country** matrices, i.e. the rows of the matrices in ``dataset``, not the columns. We therefore get:

.. code-block:: python

    >>> timeseries_dataset
        [array([[1.2,  3. , 1. , 5.4],
                 [0.1, 5.2, 4.5, 4.2],
                 [1.3, 2.3, 1. , 5.9],
                 [0.9, 4. , 4.9, 0.6],
                 [2. , 0.5, 5.9, 3.1]]),
        array([[10.2,  8.8, 11.7, 15.2],
                 [ 9.1, 12.2, 13.4, 11.7],
                 [15.4, 14. , 12.6, 15.8],
                 [11.4, 12.4, 11.7, 14.7],
                 [11.7, 16.4, 15.7, 14.9]]),
        array([[101.7,  99.7, 104.2, 103.8],
                 [105.5, 102.9, 106.5, 101.9],
                 [ 98.9, 103.2, 100.5, 104.2],
                 [ 98.4, 103.4, 104.3, 104.9],
                 [104.2, 102.3, 105. , 104.4]]),
        array([[1001.9, 1002.7, 1000.7, 1004.7],
                 [1004.4,  999.4, 1001.8, 1005.2],
                 [1000.9, 1003.8, 1002.6, 1006.6],
                 [1006.3, 1003. , 1003.4, 1002.8],
                 [ 999.6, 1003.3, 1005.3, 1003.7]])]

We now have each matrix in the list ``timeseries_dataset`` representing a country with the export time series as its
columns. This is the desired format any dataset should have in order to apply the biPCPG algorithm.

.. _correlations_info:

Computing the average correlation matrix
----------------------------------------
The input to the PCPG algorithm, which is the last step in the biPCPG algorithm, is a correlation matrix. However, a
bipartite dataset consists of a *collection* of multiple samples of data (in our toy example above, multiple countries
each exporting multiple products), so the application of the PCPG algorithm to this dataset is not straightforward.
To circumvent this problem, the approach taken in the biPCPG algorithm is to compute a correlation matrix for each
country and then take the element-wise average of these matrices. This yields a single average correlation matrix which
can then be used as the input to the PCPG algorithm.

In order to do this using the :mod:`bi_pcpg` package, we simply take the dataset in a format like
``timeseries_dataset``, this is a collection of matrices with observations (which form time series in our example) along
its columns and do the following

.. code-block:: python

    >>> from bi_pcpg.correlations import get_correlation_matrices_for_list_of_matrices
        correlation_matrices = get_correlation_matrices_for_list_of_matrices(timeseries_dataset)
        avg_correlation_matrix = np.nanmean(correlation_matrices, axis=0)

.. code-block:: python

    >>> avg_correlation_matrix
        array([[ 1.        , -0.2937555 ,  0.1195425 , -0.093738  ],
               [-0.2937555 ,  1.        ,  0.2524145 , -0.0146205 ],
               [ 0.1195425 ,  0.2524145 ,  1.        , -0.47434725],
               [-0.093738  , -0.0146205 , -0.47434725,  1.        ]])

as expect from the linearity of the time series in ``timeseries_dataset``, correlation coefficients are all equal to
one. It is important to note that ``get_correlation_matrices_for_list_of_matrices`` computes the correlations among
the **columns** of the matrices in the input list. Also, to filter the returned correlation matrices based on a
statistical T-test, we can pass the desired ``critical_value`` for the p-values, for example ``0.05``, as an argument
like this:

.. code-block:: python

    >>> filtered_correlation_matrices = get_correlation_matrices_for_list_of_matrices(timeseries_dataset,
                                                                                      critical_value=0.05)

.. code-block:: python

    >>> filtered_correlation_matrices
        [array([[ 1.      , -0.979757,       nan,       nan],
                [-0.979757,  1.      ,       nan,       nan],
                [      nan,       nan,  1.      ,       nan],
                [      nan,       nan,       nan,  1.      ]]),
        array([[ 1., nan, nan, nan],
                [nan,  1., nan, nan],
                [nan, nan,  1., nan],
                [nan, nan, nan,  1.]]),
        array([[ 1., nan, nan, nan],
                [nan,  1., nan, nan],
                [nan, nan,  1., nan],
                [nan, nan, nan,  1.]]),
        array([[ 1., nan, nan, nan],
                [nan,  1., nan, nan],
                [nan, nan,  1., nan],
                [nan, nan, nan,  1.]])]

This is mostly ``np.nan`` values given the very small sample size in our toy dataset.

Computing the PCPG network
--------------------------

Once we have a correlation matrix, or in the example above, an average correlation matrix ``avg_correlation_matrix`` we
can begin to compute the PCPG network. To do this, first instantiate the PCPG class passing the correlation matrix as an
attribute

.. code-block:: python

    >>> from bi_pcpg.pcpg import PCPG
        pcpg = PCPG(avg_correlation_matrix)

we then compute the *average influence* values among the variables in the system

.. code-block:: python

    >>> pcpg.compute_avg_influence_matrix()

.. code-block:: python


    >>> pcpg.avg_influence_matrix
        # TODO: print avg_influence_matrix

After computing the ``avg_influence_matrix`` we are able to generate the a ``networkx.DiGraph`` object of our PCPG
network by doing:

.. code-block:: python

    >>> pcpg.create_network()

.. code-block:: python

    >>> pcpg.network
        # TODO: print network object

Computing edge bootstrap values
-------------------------------

In order to assess the reliability of a PCPG network's edges we can perform a bootstrap procedure on the dataset
``timeseries_dataset``. As detailed above in :ref:`dataset_info`, this should be an iterable containing matrices whose
columns contain observations for one of the the two sets of variables in a bipartite dataset with a matrix for each
variable in the complementary set of variables.

To obtain a ``pandas.DataFrame`` containing the edge bootstrap values we simply have to do

.. code-block:: python

    >>> from bi_pcpg.bootstrap import get_bootstrap_values
        bootstrap_values = get_bootstrap_values(timeseries_dataset, num_replicates=1000)

where ``num_replicates`` is the number of replicates to be generated in the boostrap procedure. As when computing
correlations for the average correlation matrix (see :ref:`correlations_info`), a ``critical_value`` attribute could
also be passed to this function to filter correlations based on a T-test.

Note ``bootstrap_values`` is a ``pandas.DataFrame`` containing the bootstrap values of the *directed* edges in the PCPG
network. For a given entry in this dataframe, the row index is the edge's source and the column index is the edge's
target.

These bootstrap values could be added as an attribute to the network object in the class instance we obtained previously
by doing:

.. code-block:: python

    >>> pcpg.add_edge_attribute(attr_data=bootstrap_values, attr_name='bootstrap_value')

