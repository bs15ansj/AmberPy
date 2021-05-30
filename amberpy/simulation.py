#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 26

@author: bs15ansj

This module contains classes used for writing and submitting molecular 
dynamics simulation files on amber. 

MDInputs
    This is a base class used by all of the input objects.

ProductionInput
    Dataclass object storing paramaters for a production simulation in the NPT
    ensemble.
    


"""
from amberpy.crossbow import crossbow
from amberpy.utilities import get_name_from_file
import os
from typing import Union


class MDInput:
    '''Base class for MD inputs.
    Do not use this class directly, but instead, use one of the classes that 
    inherits from this class: MinimisationInput, EquilibrationInput, 
    ProductionInput. These subclasses determine which attributes will be 
    turned on/off. In theory, any valid MD flag that can be used with Amber's
    pmemd.cuda_SPFP can be given to this input object and will be written into
    the mdin file. The attributes listed here are the most common ones, but 
    please refer the Amber manual for a more detailed description 
    (https://ambermd.org/doc12/Amber21.pdf).
    
    Attributes
    ----------
    imin : int, default=0
        Flag to run minimisation. 
        
        0 = run molecular dynamics without any minimisation.
        
        1 = perform energy minimisation.
    
    maxcyc : int, default=5000 
        The maximum number of minimisation cycles to use.
    
    ncyc : int, default=2500
        The number of steepest descent minimisation cycles to use.

    irest : int, default=1
        Flag to restart from a simulation. 
        
        0 = do not restart from a simulation, instead start a new one ignoring 
        velocities and setting the timestep count to 0.
        
        1 = restart from a simulation, reading coordinates and velocities from 
        a previously saved restart file.
    
    ntx : int, default=5
        Flag to read velocities from coordinate file. 
        
        1 = read coordinates but not velocities.
        
        5 = read coordinates and velocities.
    
    ntt : int, default=3
        Flag for temperature scaling. 
        
        0 = constant total energy classsical dynamics.
        
        1 = constant temperature using the weak coupling algorithm.
        
        2 = Anderson-like temperature coupling.
        
        3 = use Langevin dynamics with a collision frequency given by gamma_ln.
        
        9 = optimized  Isokinetic  Nose-Hoover  chain  ensemble.
        
        10 = stochastic  Isokinetic  Nose-Hoover  RESPA  integrator.
        
        11 = stochastic version of Berendsen thermostat, also known as Bussi 
        thermostat

    gamma_ln : float, default=1.0
        Friction coefficient (ps^-1) when ntt=3.
        
    temp0 : float, default=310.0
        Target temperature if ntt > 0.
        
    tempi : float, default=0.0
        Initial temperature if ntt > 0. If set to 0.0, velocities are 
        calculated from the forces.

    cut : float, default=8.0 
        Non-bonded cutoff in Angstroms.

    nstlim : int, default=125000
        Total number of MD steps to peform. 
    
    dt : float, default=0.004
        Integrator time step in picoseconds.
    
    ntc : int, default=2
        Flag for SHAKE to perform bond length constraints.
        
        1 = SHAKE is not performed.
        
        2 = bonds containing hydrogen are constrained. 
        
        3 = all bonds are constrained. 
        
    ntf : int, default=2
        Flag for force evaluation (typically set ntf=ntc).
        
        1 = complete interaction calculated.
        
        2 = bond interactions involving H-atoms omitted (use with ntc=2).
        
        3 = all the bond interactions are omitted (use with ntc=3).
        
        4 = angle involving H-atoms and all bonds are omitted.
        
        5 = all bond and angle interactions are omitted.
        
        6 = dihedrals involving H-atoms and all bonds and all angle 
        interactions are omitted.
        
        7 = all bond, angle and dihedral interactions are omitted.
        
        8 = all bond, angle, dihedral and non-bonded interactions are omitted.
        
    ntpr : int, default=1000
        Write energy information to mdout and mdin files every 'ntpr' steps.
        
    ntwx : int, default=25000
        Write coordinates to trajectory every 'ntwx' steps.
        
    ntwr : int, default=10000
        Write coordinates to a restart file every 'ntwr' steps.
        
    ntwv : int, default=0
        Write velcities to an mdvel file every 'ntwv' steps. 
        
        -1 = write velocities to trajectory at an interval defined by 'ntwx'. 
        
        0 = do not write velocities.
        
    ntwf : int, default=0
        Write forces to an mdfrc file every 'ntwf' steps. 
        
        -1 = write forces to trajectory at an interval defined by 'ntwx'.
        
        0 = do not write forces.

    ntxo : int, default=2
        Restart file format. 
        
        1 = formatted (ASCII).
        
        2 = netCDF (nc, recommended).
        
    ioutfm : int, default=1
        Trajectory/velocity file format. 
        
        1 = formatted (ASCII).
        
        2 = netCDF (nc, recommended).

    iwrap : int, default=1
        Coordinate wrapping.
        
        0 = do not wrap. 
        
        1 = wrap coordinates when printing them to the same unit cell.
    
    barostat : int, default=2
        Barostat flag.
        
        1 = Berendsen.
        
        0 = Mont Carlo.
    
    ntp : int, default=0
        Flag for constant pressure dynamics. Set to >0 for NPT ensemble.
        
        0 = No pressure scaling. 
        
        1 = isotropic position scaling. 

    pres0 : float, default=1.0
        Target external pressure, in bar.

    posres : int, default=False
        Tuple of residue numbers defining start/end residues of protein chains 
        to be constrained.
        
    '''

    def __init__(self, **kwargs):
        '''
        How this class is initialised depends on which key word arguments are 
        supplied. In theory, you could call this class directly by specifying
        the all of the key word arguments that you want in the mdin file, 
        however, the preffered method would be to instantiate one of the 
        sublasses which ensure that the keyword arguments are set correctly.
        Alternatively, you can make a new input class to inherit from this and 
        set the key word arguments within it's __init__ method.
        
        Parameters
        ----------
        **kwargs
            The parameters for this argument can be set to any of the 
            attributes listed in the docstring of this class.
        '''
        
        # Set required (default) attributes
        self.ntpr: int = 1000
        self.watnam: str = "'WAT'"
        self.owtnm: str = "'O'"
        self.posres: tuple = False          
        self.cut: float = 8.0        
        self.ntxo: int = 2
        self.ntr = 1
        
        # If minimisation is turned on, enable minimisation specific attributes
        if kwargs['imin'] == 1:
            self.imin: int = 1
            self.maxcyc: int = 5000
            self.ncyc: int = 2500
        
        # If minimisation is turned off, enable simulation specific attributes
        elif kwargs['imin'] == 0:
            self.imin: int  = 0
            self.irest: int = 1
            self.ntx: int = 5
            self.ntt: int = 3
            self.gamma_ln: float = 1.0
            # If an initial temperature is given, enable the tempi attribute
            if 'tempi' in kwargs:
                self.tempi = kwargs['tempi']
            self.temp0: float = 310.0
            self.nstlim: int = 2500000
            self.dt: float = 0.004
            self.ntc: int = 2
            self.ntf: int = 2
            self.ntwx: int = 25000
            self.ntwr: int = 10000
            self.ntwv: int = 0
            self.ntwf: int = 0
            self.ioutfm: int = 1
            self.iwrap: int = 1        
        
            # If the ntp argument is given, turn on pressure control attributes
            if kwargs['ntp'] == 1:
                self.ntp: int = 1
                self.pres0: float = 1.0
                self.barostat: int = 2
        
        # Get a list of attributes. Only those that have been turned on will 
        # be in the list
        attributes = list(self.__dict__.keys())
        
        # Update attributes with any given via kwargs
        for arg in kwargs:
            if arg in attributes:
                setattr(self, arg, kwargs.get(arg))
        
        # Make a new dictionary of attributes that are turned on
        self.arg_dict = {arg : self.__dict__[arg] for arg in attributes}
    
    def write(self, out_dir, fname):
        '''Writes an mdin file containing flags for all of the turned on 
        attributes. The filename is stored in the fname attribute.
        
        Parameters
        ----------
        out_dir : str
            Directory in which the file should be written.
        fname : str
            The name of the file to be written.
        '''
        # Set fname attribute (used downstream for making HPC input files)
        self.fname = fname
        
        # Open file and write all of the turned on attributes and their values
        # in mdin format
        with open(f"{out_dir}/{fname}", "w+") as f:
            f.write("&cntrl\n")
            for var, val in self.arg_dict.items():
                # posres argument is not in the correct format so change it
                if var != "posres":
                    f.write("\t%s=%s,\n" % (var, val))
                    
            # If positional restraints are turned on, add the ntr flag and 
            # write the restraint mask
            if self.posres:
                a, b = self.posres
                f.write('\tntr=1,\n')
                f.write(f'/\nProtein posres\n1.0\nRES {a} {b}\nEND\nEND')
            else:
                f.write("/\nEND")

class MinimisationInput(MDInput):
    '''Minimisation input class. 
    Inherits attributes and methods from the MDInput class. 
    '''
    def __init__(self, **kwargs):
        '''
        Parameters
        ----------
        **kwargs
            Any attribute of the MDInput class can be provided as a key word 
            argument, however, minimisation will be turned on (simulation 
            turned off) limiting the number of attributes which can be turned 
            on. 
        ''' 
        # Turn minimisation on
        kwargs['imin'] = 1
        
        # No pressure control 
        kwargs['ntp'] = 0
        
        # Instantiate super class with key word arguments
        super().__init__(**kwargs)
    
    def __str__(self):
        '''str: The name of the input. Used for file naming.'''
        return 'minimisation'


class EquilibrationInput(MDInput):
    '''Equilibration (NVT) input class. 
    Inherits attributes and methods from the MDInput class.
    '''    
    def __init__(self, **kwargs):
        '''
        Parameters
        ----------
        **kwargs
            Any attribute of the MDInput class can be provided as a key word 
            argument, however, minimisation will be turned off (simulation 
            turned on) and pressure control will be turned off limiting the 
            number of attributes which can be turned on. 
        '''     
        
        # Turn minimisation off
        kwargs['imin'] = 0
        
        # This is not a restart from a previous simulation
        kwargs['irest'] = 0
        
        # Coordinate file does not have velocities
        kwargs['ntx'] = 1

        # Turn off ntp
        kwargs['ntp'] = 0
        
        # Make sure an initial temperature is set
        if 'tempi' not in kwargs.keys():
            kwargs['tempi'] = 0.0
        
        # Instantiate super class with key word arguments
        super().__init__(**kwargs)

    def __str__(self):
        '''str: The name of the input. Used for file naming.'''
        return 'equilibration'

class ProductionInput(MDInput):
    '''
    Production (NPT) input class. 
    Inherits attributes and methods from the MDInputclass.
    '''        
    def __init__(self, **kwargs):
        '''
        Parameters
        ----------
        **kwargs
            Any attribute of the MDInput class can be provided as a key word 
            argument, however, minimisation will be turned off (simulation 
            turned on) and pressure control will be turned off limiting the 
            number of attributes which can be turned on. 
        '''       
        
        # Turn minimisation off
        kwargs['imin'] = 0
        
        # Continue on from restart file
        kwargs['irest'] = 1
        
        # Read velocities from coordinate file
        kwargs['ntx'] = 5

        # Turn on NPT ensemble
        kwargs['ntp'] = 1
        
        # Instantiate super class with key word arguments
        super().__init__(**kwargs)
        
    def __str__(self):
        return 'production'

class Simulation:
    """Class for running MD simulations.
    
    Attributes
    ----------
    md_steps : list
        A list of MDInput objects.
        
    md_inputs : list
        A list of the input file corresponding to the input objects in 
        md_steps.
    
    name : str
        The name of the simulation, used for job naming.

    simulation_directory : str
        The name of the directory containing all of the simulation 
        input/output files.
        
    parm7 : str
        Path of the parm7 file made by tleap.
        
    rst7 : str
        Path of the rst7 file made by tleap.
        
    """
    
    def __init__(self,
                 name,
                 parm7, 
                 rst7,
                 simulation_directory=None,
                 ):
        """
        Parameters
        ----------
        name : str, optional
            The name of the simulation, used for job naming.

        parm7 : str
            Path to the parm7 input file.
            
        rst7 : str
            Path to the rst7 input file.
        
        simulation_directory : str or None
            Directory to perform the simulation in. Defaults to current 
            working directory if None
        
        """
        
        # Set attributes from arguments
        self.parm7 = parm7
        self.rst7 = rst7
        self.ref_rst7 = rst7
        self.simulation_directory = simulation_directory
        
        # If no name is given, get it from the parm7 file
        if name is None:
            name = get_name_from_file(parm7)
            
        # Add an 'a' to the jobname if it starts with a digit because arc does
        # not like them
        if name[0].isdigit():
            name = 'a'+name
        
        # Set attributes
        self.name = name
        self.md_steps = []
        self.md_inputs = []
        self.md_job_names = []
    
    def add_minimisation_step(
            self, 
            steepest_descent_steps: int = 2500,
            conjugate_gradient_steps: int = 2500,
            nb_cutoff: float = 9.0,
            restraints: Union[str, tuple] = 'protein',
            md_input: MinimisationInput = None):
        
        '''Adds a minimisation step to the simulation.
        
        Parameters
        ----------
        steepest_descent_steps : int, optional
            Number of steepest descent minimisation steps to perform.
            
        conjugate_gradient_steps : int, optional
            Number of conjugate gradient minimisation steps to perform.
            
        nb_cutoff : float, optional
            The non-bonded interaction cutoff limit in Angstroms.
            
        restraints : str or tuple, optional
            Add resraints to either the entire protein, e.g. restraints = 
            "protein", or to the residues defined by a length 2 tuple e.g. 
            restraints = (1, 500).
            
        md_input : MinimisationInput, optional
            Overrides all other parameters and instead uses a MinimisationInput
            instance.
            
        '''
        
        # If no md_input provided, build one from the key word arguments
        if md_input is None:
            kwargs = {}
            kwargs['ncyc'] = steepest_descent_steps
            kwargs['maxcyc'] = steepest_descent_steps + conjugate_gradient_steps
            kwargs['cut'] = nb_cutoff
            
            # If restraints are given process them into MDInput compatible 
            # argument 
            if restraints is not None:
                
                posres = self._restraints_from_arg(restraints)
                
                # If 'protein' is given as the restraint argument, but this 
                # class has been made directly (with Simulation() rather than
                # Experiment()) and therefore doesn't have a protein_termini
                # attribute, posres will be None so do not set protein 
                # restraints
                if posres is not None:
                    kwargs['posres'] = posres
            
            # Add a MinimisationInput object to the simulation using the key 
            # word arguments
            self.md_steps.append(MinimisationInput(**kwargs))
        
        # If Minimisation object is provided just add that
        elif isinstance(md_input, MinimisationInput):
            self.md_steps.append(md_input)
            
        else:
            raise Exception('md_input must be an instance of the MinimisationInput class or None')

    def add_equilibration_step(
            self,
            initial_temperature: float = 0.0,
            target_temperature: float = 310.0,
            nb_cutoff: float = 9.0,
            simulation_time: float = 125.0,
            restraints: Union[str, tuple] = 'protein',
            md_input: EquilibrationInput = None):
    
        '''Adds a equilibration step to the simulation.
        
        Parameters
        ----------
        inintial_temperature : float, optional
            Initial temperature to start equilibration in Kelvin.
            
        target_temperature : float, optional
            Target temperature to reach by the end of the simulation in Kelvin.
            
        nb_cutoff : float, optional
            The non-bonded interaction cutoff limit in Angstroms.
            
        simulation_time : float, optional
            Total MD simulation_time for the equilibration step in picoseconds.
            
        restraints : str or tuple, optional
            Add resraints to either the entire protein, e.g. restraints = 
            "protein", or to the residues defined by a length 2 tuple e.g. 
            restraints = (1, 500).
            
        md_input : EquilibrationInput, optional
            Overrides all other arguments and instead uses an EquilibrationInput
            instance.
            
        '''
        
        # If no md_input provided, build one from the key word arguments
        if md_input is None:
            kwargs = {}
            kwargs['tempi'] = initial_temperature
            kwargs['temp0'] = target_temperature
            kwargs['cut'] = nb_cutoff
            kwargs['dt'] = 0.001
            kwargs['nstlim'] = int(simulation_time/kwargs['dt'])
            
            # If restraints are given process them into MDInput compatible 
            # argument 
            if restraints is not None:
                
                posres = self._restraints_from_arg(restraints)
                
                # If 'protein' is given as the restraint argument, but this 
                # class has been made directly (with Simulation() rather than
                # Experiment()) and therefore doesn't have a protein_termini
                # attribute, posres will be None so do not set protein 
                # restraints
                if posres is not None:
                    kwargs['posres'] = posres
                    
            # Add a EquilibrationInput object to the simulation using the key 
            # word arguments
            self.md_steps.append(EquilibrationInput(**kwargs))
        
        # If Equilibration object is provided just add that
        elif isinstance(md_input, EquilibrationInput):
            self.md_steps.append(md_input)
            
        else:
            raise Exception('md_input must be an instance of the EquilibrationInput class or None')
            
    def add_production_step(
            self,
            timestep: float = 0.004,
            target_temperature: float = 310.0,
            nb_cutoff: float = 9.0,
            simulation_time: float = 100.0,
            md_input: EquilibrationInput = None
            ):
        
        '''Adds a Production step to the simulation.
        
        Parameters
        ----------
        timestep : float, optional
            The integrator timestep to be used in the simulation. If hydrogen
            mass repartitioning is used, set this to 0.004, otherwise set to 
            0.002 (provided that SHAKE is not turned off manually).
            
        target_temperature : float, optional
            Target temperature to be kept at in Kelvin.
            
        nb_cutoff : float, optional
            The non-bonded interaction cutoff limit in Angstroms.
            
        simulation_time : float, optional
            Total MD simulation_time for the equilibration step in nanoseconds.
            
        md_input : EquilibrationInput, optional
            Overrides all other arguments and instead uses an 
            EquilibrationInput instance.
        '''       
        
        # If no md_input provided, build one from the key word arguments
        if md_input is None:
            kwargs = {}
            kwargs['dt'] = timestep
            kwargs['cut'] = nb_cutoff
            kwargs['nstlim'] = int((1000*simulation_time)/kwargs['dt'])
            kwargs['temp0'] = target_temperature
            
            # Add a ProductionInput object to the simulation using the key 
            # word arguments            
            self.md_steps.append(ProductionInput(**kwargs))
        
        # If Production object is provided just add that
        elif isinstance(md_input, ProductionInput):
            self.md_steps.append(md_input)
            
        else:
            raise Exception('md_input must be an instance of the ProductionInput class or None')

    def run(self,
            arc = 3,
            cores = 32
            ):
        '''Writes the mdin files and runs the simulation using crossbow.

        Parameters
        ----------
        remoteworkdir : str
            Full path to the directory on arc (should be on no backup) where 
            the simulations will be performed.
            
        username : str
            Arc username for logging in via ssh.
            
        arc : int, optional
            The Arc HPC cluster you want to perform the simulations on. Can be
            3 or 4. The default is 3.
            
        cores : int, default=32
            The number of cores to use for minimisation (if minimisation is 
            used).

        '''

        # Create an empty list that will hold the inputs for each step to pass
        # to crossbow
        crossbow_inputs = []
        
        # Longbow doesn't like absolute paths so get the basenames of the 
        # input files
        parm7 = os.path.basename(self.parm7)
        rst7 = os.path.basename(self.rst7)
        ref_rst7 = os.path.basename(self.ref_rst7)
        
        # Iterate through md steps and get step number (i)        
        for i, md_step in enumerate(self.md_steps):
            i += 1
            step_name = md_step.__str__()
            
            # File name will contain the step number (based on order in 
            # md_steps) and the name of the input object. The prefix here is 
            # used by longbow to automatically generate all of the output file
            # names
            fname = f'step-{i}-{step_name}.mdin'
            
            md_step.write(self.simulation_directory, fname)
            
            # Add the filename to the md_inputs list
            self.md_inputs.append(fname)
            
            # Get the name for the job from the simulation name, step name, and 
            # step number
            step_type = md_step.__str__()
            job_name = self.name + '.' + step_type[:3] + '.' + str(i)
            self.md_job_names.append(job_name)
            
            # Get the positional arguments in a tuple. The positional arguments
            # for crossbow are (name, user, mdin, parm7, rst7, ref_rst7)
            args = (job_name, self.md_inputs[i-1], parm7, rst7, 
                    ref_rst7)
            
            # Create a key word argument dictionary for crossbow and add 
            # kwargs
            kwargs = {}
            kwargs['arc'] = arc
            kwargs['localworkdir'] = self.simulation_directory
            
            if step_type == 'minimisation':
                kwargs['minimisation'] = True
                kwargs['cores'] = cores
        
            if i != 1:
                kwargs['hold_jid'] = self.md_job_names[i-2]
            
            # Add args and kwargs as tuple to list of crossbow inputs
            crossbow_inputs.append((args, kwargs))
            
            # The rst7 variable is set to the rst7 file that comes out of this
            # step, so that the next md step can use these coordinates as an 
            # input 
            rst7 = f'step-{i}-{step_name}.rst7'
        
        for args, kwargs in crossbow_inputs:
            crossbow(*args, **kwargs)

    def _restraints_from_arg(self, arg):
        
        '''Converts restraints from argument to posres MDInput argument. 
        
        If the argument will not be a valid posres argument an execption is 
        raised.
        
        Parameters
        ----------
        arg
            Restraint argument passed to method.
        
        Returns
        -------
        restraints : tuple
            MDInput object posres parameter.
        '''
        
        if arg == 'protein':
            try:
                restraints = self.protein_termini
            except:
                restraints = None
        elif type(arg) is tuple:
            if len(arg) == 2:
                restraints = arg
            else:
                raise Exception(f'Protein restraint tuple must be length 2, not {len(arg)}')
        else:
            raise Exception(f'Restraint argument can either be "protein" or tuple, not {type(arg)}')
            
        return restraints