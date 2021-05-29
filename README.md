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

Incomplete

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
