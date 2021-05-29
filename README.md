# AmberPy

AmberPy is a tool for performing molecular dynamics simulations using Amber on the Arc High Performance Cluster (HPC) at The University of Leeds.

## Description

AmberPy makes perfoming molecular dynamics simulations simple. To run, all you need is access to a Linux machine and an account on the Arc. Setting up and running a simulation can be done wth a command as simple as:
```
amberpy [pdb_file]
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

### Installing

Incomplete

### Executing program

Incomplete

## Help

Incomplete

## Authors

Contributors names and contact info

ex. Alex St John 
ex. (https://github.com/bs15ansj)

## Version History

* 0.0.1
    * Initial Release

## License

This project is licensed under the MIT License - see the LICENSE file for details
