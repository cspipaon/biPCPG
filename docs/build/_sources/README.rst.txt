biPCPG
======

This package implements the Bipartite PCPG (biPCPG) algorithm [1]_, a generalisation of the Partial Correlation
Planar Graph (PCPG) algorithm [2]_. The PCPG is a correlation-filtering method for the construction of networks intended
for use on multivariate time series datasets with a single sample. The biPCPG framework generalises this approach to
allows its use on similar datasets containing multi-sample multivariate time series.

The biPCPG package offers three main tools:

* Handling the dataset, via the :func:`~bipcpg.utils.utils.reshape_year_matrices_to_time_series_matrices` function.
* Applying the PCPG, via the :class:`~bipcpg.pcpg.PCPG` class.
* Performing a bootstrap on the PCPG network's edges, via the :func:`~bipcpg.bootstrap.get_bootstrap_values` function.

We recommend having a look at the `tutorial <https://github.com/cspipaon/biPCPG/blob/master/docs/tutorial.rst>`_ to get
started.

References
----------

.. [1] Saenz de Pipaon Perez C, Zaccaria A, Di Matteo T. Asymmetric Relatedness from Partial Correlation. Entropy. 2022;
       24(3):365. <https://doi.org/10.3390/e24030365>

.. [2] Kenett DY, Tumminello M, Madi A, Gur-Gershgoren G, Mantegna RN, Ben-Jacob E (2010) Dominating Clasp of the
       Financial Sector Revealed by Partial Correlation Analysis of the Stock Market. PLoS ONE 5(12): e15032.
       <https://doi.org/10.1371/journal.pone.0015032>