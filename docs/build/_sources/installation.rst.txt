Installation
============

In order to install the :mod:`bipcpg` package clone (or download and unpack) the
`latest version <https://github.com/cspipaon/biPCPG>`_ from Github. From the folder containing biPCPG's setup.py file
run:

.. code-block::

    pip install .

For example:

.. code-block::

    git clone https://github.com/cspipaon/biPCPG.git
    cd biPCPG
    pip install .

To install in an Anaconda virtual environment (recommended) with the required packages:

.. code-block::

    git clone https://github.com/cspipaon/biPCPG.git
    cd biPCPG
    conda create --name <env_name> python=3.8 --file requirements.txt -c conda-forge
    conda activate <env_name>
    pip install .

where :code:`<env_name>` should be replaced by the desired name of the virtual environment.

