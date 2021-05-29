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
from amberpy.md_setup import Setup, TleapInput, PackmolInput, run_parmed
from amberpy.simulation import Simulation, MinimisationInput, EquilibrationInput, ProductionInput
from amberpy.tools import *
from amberpy.utilities import get_name_from_input_list

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
            
      
        