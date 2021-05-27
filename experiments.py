#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 16:41:36 2021

@author: bs15ansj
"""
import math
import os
from typing import Union

from amberpy.cosolvents import COSOLVENTS
from amberpy.setup import TleapInput, PackmolInput, run_parmed
from amberpy.simulation import Simulation, MinimisationInput, EquilibrationInput, ProductionInput
from amberpy.tools import *
from amberpy.utilities import get_name_from_input_list

class Setup:
    
    def __init__(self, name, protein_pdb=None, cosolvent=None, simulation_directory=os.getcwd()):
        
        # Define list of valid inputs. If adding new inputs to the class, place 
        # them in here
        input_list = [protein_pdb, cosolvent]
        
        if all(inp is None for inp in input_list):
            raise Exception('No valid inputs provided')
        
        # If no name given, generate the name from the input files
        if name is None:
            self.name = get_name_from_input_list(input_list)
        
        # Set protein_pdb attribute even if it is None so that we can let 
        # PackmolInput handle whether or not there is a protein
        self.protein_pdb = protein_pdb
            
        if cosolvent is not None:    
            self._get_cosolvent_file_names(cosolvent)
            
        self.simulation_directory = simulation_directory
        
        self.parm7 = os.path.join(self.simulation_directory, self.name) + '.parm7'
        self.rst7 = os.path.join(self.simulation_directory, self.name) + '.rst7'  
        self.tleap_pdb = os.path.join(self.simulation_directory, self.name) + '.tleap.pdb' 
        
    def run_packmol(self,
                    n_waters = None, 
                    n_cosolvents = 100, 
                    box_size = [50,50,50],
                    packmol_input = None):
        
        if packmol_input is None:
            
            if box_size is None:
                raise Exception('Please provide a box size')

            kwargs = {}
            
            kwargs['box_size'] = box_size
            kwargs['n_waters'] = n_waters
            kwargs['n_cosolvents'] = n_cosolvents
            
            packmol = PackmolInput(**kwargs)
            
        elif isinstance(packmol_input, PackmolInput):
            packmol = packmol_input
            
        else:
            raise Exception('packmol_input must be an instance of the PackmolInput class or None')
        
        packmol.run(self.cosolvent_pdb, self.packmol_pdb, self.protein_pdb)

    def run_tleap(self,
                  box_distance: float = 12.0,
                  box_shape: str = 'box',
                  ions: dict = {'Na+': 0, 'Cl-':0},
                  tleap_input: TleapInput = None):

        '''
        Solvates the pdb file and creates paramater/topology and coordinate 
        files for simulation.
        
        Parameters
        ----------
        box_distance : float
            Minimum distance between the protein and the edge of the water box.
        box_shape : str
            Shape of the simulation box. Choose from either 'box' (cuboid) or 
            'oct' (truncated octahedron).
        ions : dict
            Ions to add to the system. This should be a dictionary where the 
            keys are the ions and the values are the number of ions to add. 
            A value of 0 will attempt to neutralise the system with that ion. 
        hmr : bool
            Turn on hydrogen mass repartitioning. 
        tleap_input : TleapInput
            Overrides all other arguments and instead uses a TleapInput
            instance.
        '''
        
        if tleap_input is None:
            
            kwargs = {}

            kwargs['distance'] = box_distance
            kwargs['shape'] = box_shape
            kwargs['ions'] = ions
            
            tleap = TleapInput(**kwargs)
        
        elif isinstance(tleap_input, TleapInput):
            tleap = tleap_input
            
        else:
            raise Exception('tleap_input must be an instance of the TleapInput class or None')
        
        if hasattr(self, 'packmol_pdb'):
            tleap.run(self.packmol_pdb, self.parm7, self.rst7, self.tleap_pdb)
        else:
            tleap.run(self.protein_pdb, self.parm7, self.rst7, self.tleap_pdb)

    def run_parmed(self):

        self.hmr = True
        hmr_parm7 = self.parm7.replace('.parm7', '.HMR.parm7')
        run_parmed(self.parm7, hmr_parm7)
        self.parm7 = hmr_parm7
        
    def _get_cosolvent_file_names(self, cosolvent):
        
        # Check cosolvent is available
        if cosolvent not in COSOLVENTS.keys():
            raise Exception(f'{cosolvent} not in cosolvent directory')
            
        self.cosolvent = cosolvent
        
        # Get cosolvent type from COSOLVENTS dict
        cosolvent_type = COSOLVENTS[self.cosolvent][0]
        
        # Get cosolvent pdb file name
        self.cosolvent_pdb = COSOLVENTS[self.cosolvent][1]
        
        # If cosolvent is a small molecule, add an frcmod and mol2 file
        if cosolvent_type == 'small_molecules':
            cosolvent_mol2 = COSOLVENTS[self.cosolvent][2]
            cosolvent_frcmod = COSOLVENTS[self.cosolvent][3]
            self.frcmod_list = [cosolvent_frcmod]
            self.mol2_dict = {os.path.basename(cosolvent_mol2).split('.')[0] : cosolvent_mol2}
            
        self.packmol_pdb = os.path.join(self.simulation_directory, self.name) + '.packmol.pdb'

class Experiment(Simulation, Setup):
    
    def __init__(self, name, replica_name, protein_pdb=None, cosolvent=None):

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
            self.simulation_directory = os.path.join(os.getcwd(), dirname, str(self.replica_name))
            self.root_directory = os.path.join(os.getcwd(), dirname)
    
            try:
                os.mkdir(self.root_directory)
            except FileExistsError:
                pass
    
            try:
                os.mkdir(self.simulation_directory)
            except FileExistsError:
                pass  
            
        else:
            self.simulation_directory = os.path.join(os.getcwd(), dirname)
            self.root_directory = os.path.join(os.getcwd(), dirname)
            if not os.path.isdir(self.simulation_directory):
                os.mkdir(self.simulation_directory)
    
        Setup.__init__(self, self.name, protein_pdb, cosolvent, self.simulation_directory)
        
        Simulation.__init__(self, self.name, self.parm7, self.rst7, self.simulation_directory)
    @property 
    def protein_termini(self):
        return get_protein_termini(self.tleap_pdb)
        
class ProteinSimulation(Experiment):
    
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

class CosolventSimulation(Experiment):
    
    def __init__(self, cosolvent, name = None, replica_name = None):

        Experiment.__init__(self, name, replica_name, cosolvent=cosolvent)
            
    def make_system(self,
                    n_waters = None, 
                    n_cosolvents = 100, 
                    box_size = [50,50,50],
                    ions: dict = {'Na+': 0, 'Cl-':0},
                    distance: float = 12.0,
                    hmr: bool = True,
                    packmol_input = None):
        
        self.run_packmol(n_waters, n_cosolvents, box_size, packmol_input)
        
        if n_waters is None:
            self.run_tleap(tleap_input=TleapInput(distance=0.0, ions=ions))
        elif type(n_waters) is int:
            self.run_tleap(tleap_input=TleapInput(ions=ions, solvate=False, box_size=box_size))
        else:
            raise Exception('n_waters must be an integer or None')
        
        if hmr:
            self.run_parmed()                 
        
class ProteinCosolventSimulation(CosolventSimulation, ProteinSimulation):
    
    def __init__(self, protein_pdb, cosolvent, name = None, replica_name = None):
        
        Experiment.__init__(self, name, replica_name, protein_pdb=protein_pdb, cosolvent=cosolvent)
            
      
        