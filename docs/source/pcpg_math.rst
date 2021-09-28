Partial Correlation Planar Algorithm
------------------------------------

The Partial Correlation Planar Graph (PCPG) [1]_ is based on *partial correlation* which measures the effect that a
random variable :math:`Z` has on the correlation between two other random variables :math:`X` and :math:`Y`. The partial
correlation is defined in terms of the Pearson correlations :math:`\rho(\cdot, \cdot)` between the three variables as

.. math::

    \rho(X, Y: Z)=\frac{\rho(X, Y)-\rho(X, Z) \rho(Y, Z)}{\sqrt{\left[1-\rho^{2}(X, Z)\right]\left[1-\rho^{2}(Y, Z)\right]}}.

A small value of :math:`\rho(X, Y: Z)` may be ambiguous, as this could be due to the correlations among the three
variables being small; or due to variable :math:`Z` having a strong effect on the correlation between :math:`X` and
:math:`Y`, which is generally the interesting case. In order to discriminate between these two cases the
*correlation influence* or *influence* of variable :math:`Z` on the pair of elements :math:`X` and :math:`Y` is used.
This is defined as

.. math::
    d(X, Y: Z) \equiv \rho(X, Y)-\rho(X, Y: Z).

Finally, the metric on which the PCPG is built is the *average influence* of variable :math:`Z` on the
correlations between :math:`X` and all other variables in the system. This is given by

.. math::
    d(X: Z)=\langle d(X, Y: Z)\rangle_{Y \neq X}.


An important detail is that, in general, :math:`d(X: Z) \neq d(Z: X)`. The largest among these two quantities indicates
the main direction of influence between :math:`X` and :math:`Z`, as influence is generally bidirectional. The
difference between these two values are often small, which makes a bootstrap procedure necessary in order to asses the
confidence in the direction of the average influence, as well as the average influence values.

The construction algorithm of a PCPG network starts with a list of the :math:`N(N-1)` average influence values in decreasing
order and an empty graph of $N$ nodes and no edges, where :math:`N` is the number of variables in the system. We then cycle
through the sorted list, starting with the largest average influence value found, e.g. :math:`d(J: I)`. The edge
:math:`I \to J` is
included in the network if and only if the resulting network is still planar and the edge :math:`J \to I` has not been
included already.
We stop adding edges if adding the next edge in the list would break the planarity of the graph. This procedure ensures
two things: (i)  only the largest among :math:`d(X: Z)` and :math:`d(Z: X)` will be included in the network, and (ii) the final
network has :math:`3(N-2)` edges. The end result of this procedure is what we refer to as the PCPG network, :math:`G`.
Naturally, we also obtain the average influence :math:`d` associated to each edge in :math:`G`, as well as the
network's adjacency matrix :math:`\mathbf{A}` defined as

.. math::

    A_{I, J} =
        \begin{cases}
            1 & \text{if} \ \text{edge} \ I \to J \in G, \\
            0 & \text{otherwise}.
        \end{cases}

References
----------

.. [1] Kenett DY, Tumminello M, Madi A, Gur-Gershgoren G, Mantegna RN, Ben-Jacob E (2010) Dominating Clasp of the
       Financial Sector Revealed by Partial Correlation Analysis of the Stock Market. PLoS ONE 5(12): e15032.
       <https://doi.org/10.1371/journal.pone.0015032>