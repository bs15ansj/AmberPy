Getting Started
===============

Creating a new environment and installing AmberTools
----------------------------------------------------

AmberPy currently depends on the Longbow package, which can only be run on python versions 2.7, 3.5, 3.6, and 3.7. We therefore recommend using python 3.7. 

The easiest (and safest) way to prepare for your AmberPy installation is to create a new environment using Anaconda. If you haven’t already installed Anaconda you can download the installer here https://www.anaconda.com/. Once Anaconda is installed create a new Anaconda environment with:

.. code-block:: console

   username@machine:~$ conda create --name amberpy python=3.7

Once the environment is created, activate it with:

.. code-block:: console

   username@machine:~$ conda activate amberpy

Once activated, you should now be in your base environment and your terminal command line should look something like this:

.. code-block:: console

   (amberpy) username@machine:~$

This environment is completely separate to your main (base) environment and cannot share and packages you install with it. You should always be in this environment when working on/using AmberPy. To leave the environmet simply type:

.. code-block:: console
    
   (amberpy) username@machine:~$ conda deactivate

AmberPy also depends on AmberTools. You can install AmberTools within your Anaconda environment with:

.. code-block:: console

   (amberpy) username@machine:~$ conda install -c conda-forge ambertools=21 compilers

Once you have created your environment and installe AmberTools, you are ready to install AmberPy.

Arc Configuration
-----------------

If you already have an account on Arc and a directory on /nobackup, and can log into arc3 and arc4 without entering your password, skip this step. 

In order to run MD simulations with AmberPy, you must have an account on the Arc HPC at the University of Leeds. To get an account (for students and staff only), apply on the website https://arc.leeds.ac.uk/. Once you have an account, open your ssh configuration file in a text editor:

.. code-block:: console

   username@machine:~$ gedit ~/.ssh/config

and add these lines:

.. code-block:: console

  Host arc4
    HostName arc4.leeds.ac.uk
    ProxyCommand ssh -W %h:%p remote-access.leeds.ac.uk

  Host arc3
    HostName arc3.leeds.ac.uk
    ProxyCommand ssh -W %h:%p remote-access.leeds.ac.uk

This will enable you to log in to arc3 or arc4 directly with the commands:

.. code-block:: console

   username@machine:~$ ssh [username]@arc3 

or 

.. code-block:: console

   username@machine:~$ ssh [username]@arc4 

When you try to log into arc3 or arc4 with the commands above, you will be asked to enter your password. You can configure your login such that you don’t have to enter a password each time. First generate an ssh key with:

.. code-block:: console

   username@machine:~$ ssh-keygen

You can keep hitting enter when it asks you questions. Then, copy your key first to the proxy (remote-access.leeds.ac.uk):

.. code-block:: console

   username@machine:~$ ssh-copy-id remote-access.leeds.ac.uk

then to arc3 and arc4

.. code-block:: console

   username@machine:~$ ssh-copy-id arc3
   username@machine:~$ ssh-copy-id arc4

You should now be able to log into arc3/4 without having to enter your password.


Installing
----------

To install AmberPy, first make sure you are in your correct environment then clone this repository with:

.. code-block:: console
    
   (amberpy) username@machine:~$ git clone https://github.com/pacilab/AmberPy.git

Then, change to the cloned directory:

.. code-block:: console
    
   (amberpy) username@machine:~$ cd AmberPy

and type:

.. code-block:: console
    
   (amberpy) username@machine:~/AmberPy$ pip install -e .

You will now have access to AmberPy anywhere on your computer (you don't need to be in the AmberPy directory to use it).

Finally, you may need to edit the configuration file that is created during installation at ``~/.amberpy/hosts.conf``. This file provides Longbow with the inputs needed to run on Arc. The only variables that you may need to change are ``user`` and/or ``remoteworkdir``. By default, these will be set to your username on the computer that you are using, and a directory with that username on ``/nobackup``. If your username/directory are different to this, then edit these variables. 

Using AmberPy
-------------

AmberPy is designed to be used by anyone with access to an Arc account and a Linux machine, from beginner to advanced. There are different levels of complexity that can be employed to run your simulations:

* Level 1: You just want to run a simple simulation using all of the defaults to make a nice movie of a protein. No python needed.

* Level 2: You know a little python and want to be able to modify basic simulation settings; simulation time, temperature, salt concentration etc. 

* Level 3: You know a little python but want to have more control over your MD set up and simulation.

* Level 4: You are a python programmer and would like to create your own classes to have more control over how your simulations are set up and run.

* Level 5: You are a python developer and want to contribute to this repository. 

The following will give a brief descritpion on how to run and use AmberPy at each level.

Level 1
*******

In order to run a very simple program that comes with AmberPy called ``james``, all you need to do is type:

.. code-block:: console
    
   (amberpy) username@machine:~$ james [pdb_file]

where [pdb_file] is the name of the pdb file in your directory that you want to simulate. 

The are few more options you can use with this program. Type:

.. code-block:: console
    
   (amberpy) username@machine:~$ james --help

to see them.

Level 2
*******

You can make a simple python script to set up and run simulations by first importing an experiment from the ``amberpy.experiments`` module e.g.:

.. code-block:: python

   from amberpy.experiments import ProteinExperiment

There are three types of experiments that are currently available in AmberPy out of the box: ``ProteinExperiment``, ``CosolventExperiment``, and ``ProteinCosolventExperiment`` (the nature of each being self explanatory).

Then, you would initialise an object of the experiment e.g.:

.. code-block:: python

   experiment = ProteinExperiment([pdb_file])

The required arguments for each experiment depend on which one you are using. A ``ProteinExperiment`` requires a pdb file, a ``CosolventExperiment`` requires the name of a cosolvent (see supported cosolvents), and a ``ProteinCosolventExperiment`` requires both a pdb file and the name of a cosolvent. 

You can also (optionally) specify the name of the experiment and/or a replica name (if you're creating multiple copies of an experiment and want the files and directories to be separated):

.. code-block:: python

   experiment = ProteinExperiment([pdb_file], name='my_experiment', replica_name='1')

Next, you will call the ``make_system`` method on your experiment to create the files needed for the simulation. For a ProteinExperiment, this will create a water box around the protein, add ions to the box, and generate paramater/topology and coordinate files that can be read by the simulation software. If you call the ``make_system`` method without any arguments, AmberPy will just use the defaults:

.. code-block:: python

  # Creates a cubic box whose edges are at least 12 Angstroms away from the protein and adds sodium 
  # and chloride ions to neutralise the system.
  experiment.make_system()

You can also specify the arguments yourself. The code below is exactly equivalent to the code above (defaults are just specified). 

.. code-block:: python

   # Creates a cubic box whose edges are at least 12 Angstroms away from the protein and adds sodium 
   # and chloride ions to neutralise the system.
   experiment.make_system(box_distance=12.0, box_shape='box', ions={'Na+': 0, 'Cl-':0})
   
The argument box_distance can be any positive number, box_shape can be either 'box' for a cubic box, or 'oct' for a truncated octahedron, and ions must be a dictionary containing the names of the ions you want to add as elements, and the number of each of the ions you want to add as values. Specifying 0 ions simply tells AmberPy to attempt to neutralise the system with that ion. 

After you have made your system, you'll need to add some molecular dynamics steps. Typically, this consists of a minimisation step (remove any bad clashes/angles etc.), and equilibration step (to heat the system up), and a production step (the main simulation step that you will look at/analyse):

.. code-block:: python

   experiment.add_minimisation_step()
   experiment.add_equilibration_step()
   experiment.add_production_step()

Again, you can add your own arguments here if you want. The main part that you may want to change is the simulation time in the production step, as this really depends on how time constrained you are. Typically, you can expect to get around 100-300 ns/day of simulation time using Amber on Arc. Below is another example of how you could add your simulation steps (again using defaults which you are free to change):

.. code-block:: python

   experiment.add_minimisation_step(steepest_descent_steps=2500, conjugate_gradient_steps=2500, nb_cutoff=9.0, restraints='protein')
   experiment.add_equilibration_step(initial_temperature=0.0, target_temperature=310.0, nb_cutoff=9.0, restraints='protein', simulation_time=125.0)
   experiment.add_production_step(timestep=0.004, target_temperature=310.0, nb_cutoff=9.0, simulation_time=100.0)

For the minimisation step, you probably won't need to change anything. The arguments ``steepest_descent`` and ``conjugate_gradient`` simply tell Amber how many minimisation steps of each of the respective algorithms it should run (see the Amber manual for more details https://ambermd.org/doc12/Amber21.pdf). The ``nb_cutoff`` parameter (which is used by all steps and should be the same for each) tells Amber at what distance it should stop calculating non-bonded (electrostatic, VdW) interactions between atoms. Lowering this value may speed up your simulation since fewer calculations need to be made during each step, but will decrease the accuracy. The ``restraints`` argument places positional restraints on the protein (if you set ``restraints='protein'``). If instead you provide a tuple to this argument, restraints will be placed on a range of residues specified by the tuple, for example, ``restraints=(1,100)`` places positional restraints on residues 1 to 100. For most cases you can leave the restraints as they are (applied to the protein) since you probably don't want your protein to move too much during minimisation and equilibration. 

For the equilibration step you have the option to specify ``initial_temperature`` and ``target_temperature`` in Kelvin. You can also specify ``simulation_time`` in picoseconds. 

For the production step, you have the option of specifying ``timestep``. The timestep is the time between each calculation in the simulation and should be set to 0.004 if the masses of your hydrogens have been repartitioned, or 0.002 if they have not. You can also specify the ``simulation_time`` in nanoseconds. 

Once you have added the molecular dynamics steps you can run the simulation using the ``run`` method. This method takes two required arguments; your username on Arc and your ``/nobackup`` directory on arc:

.. code-block:: python

   experiment.run([username], /path/to/your/nobackup/directory)

In addition, the arguments arc and cores can be used to specify which version of arc you want, and how many cores to used for minimisation:

.. code-block:: python

   experiment.run([username], /path/to/your/nobackup/directory, arc=3, cores=32)


When you have finished writing your script, simply run it with:

.. code-block:: console

   (amberpy) username@machine:~$ python [name_of_your_script].py

Level 3
*******

If you are already comfortable with using Amber to set up and run molecular dynamics simulations, then you may want to directly specify particular commands. AmberPy uses three programs from Amber; Packmol, Tleap and pmemd. Instead of providing arguments to experiment methods, you can provide an one of the following input classes:

* PackmolInput

* TleapInput

* MinimisationInput

* EquilibrationInput

* ProductionInput

These inputs provide a wider range of arguments than those provided in the experiment methods. For example, if you wanted to add a ligand to your system you could use the ``frcmod_list`` and ``mol2_dict`` arguments to create a TleapInput instance, and then provide that to your ``make_system`` method:

.. code-block:: python

   tleap_input = TleapInput(frcmod_list=['frcmod.ligand'], mol2_dict={'LIG', 'ligand.mol2'})

   experiment = ProteinExperiment('protein_and_ligand.pdb')
   experiment.make_system(tleap_input=tleap_input)

If you want to see a full description of all of the input classes and what arguments they can take, please see the API reference.







