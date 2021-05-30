#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from amberpy.md_setup import Setup, TleapInput, PackmolInput
from amberpy.simulation import Simulation
from amberpy.tools import get_protein_termini
from amberpy.utilities import get_name_from_input_list

class Experiment(Setup, Simulation):
    '''Base class for setting up and running an experiment. 
    This class inherits from both the Simulation and Setup classes.
    
    This class is intended to be inherited from by other classes that perform 
    specific tasks e.g. ProteinExperient, CosolventExperiment, 
    ProteinCosolventExperiment. If you want to make your own type of 
    experiment then you should inherit from this class.

    Attributes
    ----------
    name : str
        The name of the experiment. 
        
    replica_name : str
        The name of the replica (if this experiment is a replica).
    
    directory : str
        The directory in which the experiment will take place.
        
    root_directory : str
        The root directory containing all of the experiment directories if this
        experiment is a replica.
    '''
    
    def __init__(self, name, replica_name=None, protein_pdb=None, cosolvent=None):
        '''
        Parameters
        ----------
        name : str
            The name to call the experiment. The name is required as it is 
            assumed that name generation will be handled by objects inheriting
            from this class. 
            
        replica_name : str or None, default=None
            The name to call the replica (if this experiment is a replica). If 
            this is not a replica then leave as the default, None.
            
        protein_pdb : str, default=None
            Path to the protein_pdb file to be simulated.
            
        cosolvent : str, default=None
            Three letter name of the cosolvent to be simulated. Available 
            names are any pdb file names in the amberpy/cosolvent 
            sub-directories.

        Raises
        ------
        Exception
            Raises an exception if no inputs are provided.

        '''

        # Define list of valid inputs. If adding new inputs to the class, place 
        # them in here
        input_list = [protein_pdb, cosolvent]
        
        if all(inp is None for inp in input_list):
            raise Exception('No valid inputs provided')
        
        # If no name given, generate the name from the input files
        if name is None:
            self.name = get_name_from_input_list(input_list)
            
        self.replica_name = replica_name
        
        # If not already made, create directory based on name/replica name
        dirname = self.name.replace('.','')
        if self.replica_name is not None:
            self.directory = os.path.join(os.getcwd(), dirname, str(self.replica_name))
            self.root_directory = os.path.join(os.getcwd(), dirname)
    
            try:
                os.mkdir(self.root_directory)
            except FileExistsError:
                pass
    
            try:
                os.mkdir(self.directory)
            except FileExistsError:
                pass  
            
        else:
            self.directory = os.path.join(os.getcwd(), dirname)
            self.root_directory = os.path.join(os.getcwd(), dirname)
            if not os.path.isdir(self.directory):
                os.mkdir(self.directory)
    
        Setup.__init__(self, self.name, protein_pdb, cosolvent, self.directory)
        
        Simulation.__init__(self, self.name, self.parm7, self.rst7, self.directory)
        
    @property 
    def protein_termini(self):
        '''tuple : Terminal residues in tleap_pdb file associated with the 
        experiment.
        '''
        try:
            return get_protein_termini(self.tleap_pdb)
        except AttributeError:
            raise Exception('This experiment object does not have a tleap_pdb'
                            ' file associated with it needed to calculate '
                            'obtain the protein termini.')
        
class ProteinExperiment(Experiment):
    
    def __init__(self, protein_pdb, name = None, replica_name = None):

        Experiment.__init__(self, name, replica_name, protein_pdb=protein_pdb)
        
    def make_system(self,
                    box_distance: float = 12.0,
                    box_shape: str = 'box',
                    ions: dict = {'Na+': 0, 'Cl-':0}, 
                    hmr: bool = True,
                    tleap_input: TleapInput = None):
        
        self.run_tleap(box_distance, box_shape, ions, tleap_input)
        
        if hmr:
            self.run_parmed()

class CosolventExperiment(Experiment):
    
    def __init__(self, cosolvent, name = None, replica_name = None):

        Experiment.__init__(self, name, replica_name, cosolvent=cosolvent)
            
    def make_system(self,
                    n_waters = None, 
                    n_cosolvents = 100, 
                    box_size = [50,50,50],
                    ions: dict = {'Na+': 0, 'Cl-':0},
                    distance: float = 12.0,
                    hmr: bool = True,
                    packmol_input: PackmolInput = None):
        
        self.run_packmol(n_waters, n_cosolvents, box_size, packmol_input)
        
        if n_waters is None:
            self.run_tleap(tleap_input=TleapInput(distance=0.0, ions=ions))
        elif type(n_waters) is int:
            self.run_tleap(tleap_input=TleapInput(ions=ions, solvate=False, box_size=box_size))
        else:
            raise Exception('n_waters must be an integer or None')
        
        if hmr:
            self.run_parmed()                 
        
class ProteinCosolventExperiment(CosolventExperiment, ProteinExperiment):
    
    def __init__(self, protein_pdb, cosolvent, name = None, replica_name = None):
        
        Experiment.__init__(self, name, replica_name, protein_pdb=protein_pdb, cosolvent=cosolvent)
            
      
        