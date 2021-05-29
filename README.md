# AmberPy

AmberPy is a tool for performing molecular dynamics simulations using Amber on the Arc High Performance Cluster (HPC) at The University of Leeds.

## Description

AmberPy makes perfoming molecular dynamics simulations simple. To run, all you need is access to a Linux machine and an account on the Arc. Setting up and running a simulation can be done wth a command as simple as:
```
james [pdb_file]
```

Alternatively, AmberPy can be used as a python library to perform simulations using a script as simple as:
```
from amberpy.experiments import ProteinSimulation
p = ProteinSimulation([pdb_file])
p.make_system()
p.add_minimisation_step()
p.add_equilibration_step()
p.add_production_step()
p.run()
```
This tool is intended to be used by students and staff at the University of Leeds, since an account on Arc is required. In the future, we hope to extend this to users with access to other HPCs. 

## Getting Started

### Dependencies

AmberPy currently depends on the Longbow package, which can only be run on python versions 2.7, 3.5, 3.6, and 3.7. We therefore recommend using python 3.7 to run longbow. 

The easiest (and safest) way to prepare for your AmberPy installation is to create a new environment using Anaconda. If you haven’t already installed Anaconda you can download the installer here https://www.anaconda.com/. Once Anaconda is installed create a new Anaconda environment with:
```
conda create --name amberpy python=3.7
```
Once the environment is created, activate it with:
```
conda activate amberpy
```
You will now be in an environment called 'amberpy' (it should say (amberpy) before your username in the terminal). This environment is completely separate to your base environment and cannot share and packages you install with it. You should always be in this environment when working on/using AmberPy. To leave the environmet simply type:
```
conda deactivate
```

AmberPy also depends on AmberTools. You can install AmberTools within your Anaconda environment with:
```
conda install -c conda-forge ambertools=21 compilers
```
if you are in your amberpy environment, or:
```
conda install --name amberpy 
```
if you are not in your environment. 

Once you have created your environment and installe AmberTools, you are ready to install AmberPy.

#### Arc Configuration

If you already have an account on Arc and a directory on /nobackup, skip this step. 

In order to run MD simulations with AmberPy, you must have an account on the Arc HPC at the University of Leeds. To get an account (for students and staff only), apply on the website https://arc.leeds.ac.uk/. Once you have an account, open your ssh configuration file in a text editor:
```
gedit ~/.ssh/config
```
and add these lines:
```
Host arc4
  HostName arc4.leeds.ac.uk
  ProxyCommand ssh -W %h:%p remote-access.leeds.ac.uk

Host arc3
  HostName arc3.leeds.ac.uk
  ProxyCommand ssh -W %h:%p remote-access.leeds.ac.uk
```
This will enable you to log in to arc3 or arc4 directly with the commands:
```
ssh [username]@arc3 
```
or 
```
ssh [username]@arc4
```
where [username] is your username on Arc. 

When you try to log into arc3 or arc4 with the commands above, you will be asked to enter your password. You can configure your login such that you don’t have to enter a password each time. First generate an ssh key with:
```
ssh-keygen
```
You can keep hitting enter when it asks you questions. Then, copy your key first to the proxy (remote-access.leeds.ac.uk):
```
ssh-copy-id remote-access.leeds.ac.uk
```
then to arc3 and arc4
```
ssh-copy-id arc3
ssh-copy-id arc4
```
You should now be able to log into arc3/4 without having to enter your password. 

### Installing

To install AmberPy, first make sure you are in your correct environment then clone this repository with:
```
git clone https://github.com/pacilab/AmberPy.git
```
Then, change to the cloned directory:
```
cd AmberPy
```
and type:
```
python setup.py install
```
You will now have access to AmberPy anywhere on your computer (you don't need to be in the AmberPy directory to use it).


### Executing program

AmberPy is designed to be used by anyone with access to an Arc account and a Linux machine, from beginner to advanced. There are different levels of complexity that can be employed to run your simulations:
* Level 1: You just want to run a simple simulation using all of the defaults to make a nice movie of a protein. No python needed.
* Level 2: You know a little python and want to be able to modify basic simulation settings; simulation time, temperature, salt concentration etc. 
* Level 3: You know a little python but want to have more control over your MD set up and simulation.
* Level 4: You are a python programmer and would like to create your own objects to have more control over how your simulations are set up and run.
* Level 5: You are a python developer and want to contribute to this repository. 

The following will give a brief descritpion on how to run and use AmberPy at each level.

#### Level 1
In order to run a very simple program that comes with AmberPy called james, all you need to do is type 
```
james [pdb_file]
```
where [pdb_file] is the name of the pdb file in your directory that you want to simulate. If it's your first time running the program, you'll need to use the --remote_working_directory flag to add the path to your nobackup directory on arc where you want to run your simulations:
```
james [pdb_file] --remote_working_directory /path/to/your/nobackup/directory
```
You only need to specify use this flag during your first run, after which a file will appear at ~/.amberpy/remoteworkdir.conf containing your remote working directory path so you don't have to specify it again. 

The are few more options you can use with this program. Type:
```
james --help
```
to see them.

#### Level 2
You can make a simple python script to set up and run simulations by first importing an experiment amberpy.experiments module e.g.:
```
from amberpy.experiments import ProteinSimulation
```
There are three types of experiments that are currently available in AmberPy out of the box: ProteinSimulation, CosolventSimulation, and ProteinCosolventSimulation (the nature of each being self explanatory).

Then, you would initialise an object of the experiment e.g.:
```
experiment = ProteinSimulation([pdb_file])
```
The required arguments for each experiment depend on which one you are using. A ProteiSimulation requires a pdb file, a CosolventSimulation requires the name of a cosolvent (see supported cosolvents), and a ProteinCosolventSimulation requires both a pdb file and the name of a cosolvent. 

You can also (optionally) specify the name of the experiment and/or a replica name (if you're creating multiple copies of an experiment and want the files and directories to be separated):
```
experiment = ProteinSimulation([pdb_file], name='my_experiment', replica_name='1')
```

Next, you will call the .make_system() method on your experiment to create the files needed for the simulation. For a ProteinSimulation, this will create a water box around the protein, add ions to the box, and generate paramater/topology and coordinate files that can be read by the simulation software. If you call the .make_system() method without any arguments, AmberPy will just use the defaults:
```
# Creates a cubic box whose edges are at least 12 Angstroms away from the protein and adds sodium 
# and chloride ions to neutralise the system.
experiment.make_system()
```
You can also specify the arguments yourself. The code below is exactly equivalent to the code above (defaults are just specified). 
```
# Creates a cubic box whose edges are at least 12 Angstroms away from the protein and adds sodium 
# and chloride ions to neutralise the system.
experiment.make_system(box_distance=12.0, box_shape='box', ions={'Na+': 0, 'Cl-':0})
```
The argument box_distance can be any positive number, box_shape can be either 'box' for a cubic box, or 'oct' for a truncated octahedron, and ions must be a dictionary containing the names of the ions you want to add as elements, and the number of each of the ions you want to add as values. Specifying 0 ions simply tells AmberPy to attempt to neutralise the system with that ion. 

After you have made your system, you'll need to add some molecular dynamics steps. Typically, this consists of a minimisation step (remove any bad clashes/angles etc.), and equilibration step (to heat the system up), and a production step (the main simulation step that you will look at/analyse):
```
experiment.add_minimisation_step()
experiment.add_equilibration_step()
experiment.add_production_step()
```
Again, you can add your own arguments here if you want. The main part that you may want to change is the simulation time in the production step, as this really depends on how time constrained you are. Typically, you can expect to get around 100-300 ns/day of simulation time using Amber on Arc. Below is another example of how you could add your simulation steps (again using defaults which you are free to change):
```
experiment.add_minimisation_step(steepest_descent_steps=2500, conjugate_gradient_steps=2500,
                                 nb_cutoff=9.0, restraints='protein')
experiment.add_equilibration_step(initial_temperature=0.0, target_temperature=310.0, 
                                 nb_cutoff=9.0, restraints='protein', simulation_time=125.0)
experiment.add_production_step(timestep=0.004, target_temperature=310.0, nb_cutoff=9.0,
                               simulation_time=100.0)
```
For the minimisation step, you probably won't need to change anything. The arguments steepest_descent and conjugate_gradient simply tell Amber how many minimisation steps of each of the respective algorithms it should run (see the Amber manual for more details https://ambermd.org/doc12/Amber21.pdf). The nb_cutoff parameter (which is used by all steps and should be the same for each) tells Amber at what distance it should stop calculating non-bonded (electrostatic, VdW) interactions between atoms. Lowering this value may speed up your simulation since fewer calculations need to be made during each step, but will decrease the accuracy. The restraints argument places positional restraints on the protein (if you set restraints='protein'). If instead you provide a tuple to this argument, restraints will be placed on a range of residues specified by the tuple, for example:
```
restraints=(1,100)
```
places positional restraints on residues 1 to 100. For most cases you can leave the restraints as they are (applied to the protein) since you probably don't want your protein to move too much during minimisation and equilibration. 
For the equilibration step you have the option to specify an initial and target temperature in Kelvin. You can also specify the equilibration time in picoseconds. 
For the production step, you have the option of specifying the timestep. The timestep is the time between each calculation in the simulation and should be set to 0.004 if the masses of your hydrogens have been repartitioned, or 0.002 if they have not. You can also specify the simulation time in nanoseconds. 

Once you have added the molecular dynamics steps you can run the simulation using the run() method. This method takes two required arguments; your username on Arc and your /nobackup directory on arc:
```
experiment.run([username], /path/to/your/nobackup/directory)
```
In addition, the arguments arc and cores can be used to specify which version of arc you want, and how many cores to used for minimisation:
```
experiment.run([username], /path/to/your/nobackup/directory, arc=3, cores=32)
```

When you have finished writing your script, simply run it with:
```
python [name_of_your_script].py
```

## Help

Incomplete

## Authors

Contributors names and contact info

Alex St John (bs15ansj@leeds.ac.uk)

## Version History

* 0.0.1
    * Initial Release

## License

This project is licensed under the MIT License - see the LICENSE file for details
