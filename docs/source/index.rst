Welcome to AmberPy's documentation!
===================================

AmberPy is a tool for performing molecular dynamics simulations using Amber on the Arc High Performance Cluster (HPC) at The University of Leeds.

AmberPy makes perfoming molecular dynamics simulations simple. To run, all you need is access to a Linux machine and an account on the Arc. Setting up and running a simulation can be done wth a command as simple as:


.. code-block:: console

   $ james [pdb_file]

Alternatively, AmberPy can be used as a python library to perform simulations using a script as simple as:

.. code-block:: python

   from amberpy.experiments import ProteinExperiment
   p = ProteinExperiment([pdb_file])
   p.make_system()
   p.add_minimisation_step()
   p.add_equilibration_step()
   p.add_production_step()
   p.run() 

This tool is intended to be used by students and staff at the University of Leeds, since an account on Arc is required. In the future, we hope to extend this to users with access to other HPCs. 

.. toctree::
   :maxdepth: 4
   :caption: Contents

   getting_started
   experiment

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
