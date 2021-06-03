#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  5 11:12:13 2020

@author: bs15ansj
"""
import tempfile
from subprocess import PIPE, Popen
import os
from amberpy.tools import get_max_distance
from amberpy.utilities import get_name_from_input_list
import amberpy.cosolvents as cosolvents_dir
from amberpy.cosolvents import COSOLVENTS

class TleapInput:
    '''
    Tleap Input object
    '''
    def __init__(
            self,
            protein_forcefield: str = "ff19SB",
            water_forcefield: str = "tip3p",
            solvate: bool = True,
            shape: str = "box",
            distance: float = 12.0,
            distance_from_residues: tuple = None,
            ions: dict = {
                "Na+": 0,
                "Cl-": 0
            },
            save_protein: bool = True,
            ions_rand: bool = True,
            box_size: float = None,
            no_centre: bool = False,
            frcmod_list=None,
            mol2_dict=None
    ):
        
        self.protein_forcefield = protein_forcefield
        self.water_forcefield = water_forcefield
        self.solvate = solvate
        self.distance = distance
        self.distance_from_residues = distance_from_residues
        self.ions = ions
        self.save_protein = save_protein
        self.shape = shape
        self.ions_rand = ions_rand
        self.frcmod_list = frcmod_list
        self.mol2_dict = mol2_dict
        
        if box_size is not None:
            if type(box_size) is int:
                box_size = float(box_size)
                
            if type(box_size) is float:    
                self.box_size = [box_size, box_size, box_size]
            elif type(box_size) is list:
                if len(box_size) != 3:
                    raise Exception('Please provide either 1 number or list of 3'+
                                    ' numbers for box size')
                else:
                    self.box_size = [float(x) for x in box_size]
            else:
                raise Exception('Please provide either 1 number or list of 3'+
                                ' numbers for box size')
        else:
            self.box_size = None
            
        self.no_centre = no_centre
        
    def run(
            self,
            pdb,
            parm7_out,
            rst7_out,
            pdb_out=None
    ):
        

        tleap_lines = f"source leaprc.protein.{self.protein_forcefield}\n"

        if self.solvate or self.box_size:
            tleap_lines += f"source leaprc.water.{self.water_forcefield}\n"
            
        if not self.frcmod_list is None:
            for frcmod in self.frcmod_list:
                if not frcmod is None:
                    tleap_lines += f"loadamberparams {frcmod}\n"
        
        if not self.mol2_dict is None:
            for name, mol2 in self.mol2_dict.items():
                if not mol2 is None:
                    tleap_lines += f"{name} = loadmol2 {mol2}\n"
            
        if not pdb is None:
            tleap_lines += f"mol = loadpdb {pdb}\n"

        if self.solvate:
            distance = self.distance
                
            if self.distance_from_residues:
                start, stop, distance = self.distance_from_residues
                d1 = get_max_distance(pdb, residues=(start, stop))
                d2 = get_max_distance(pdb)
                distance -= (d2 - d1)/2
            tleap_lines += f"solvate{self.shape} mol TIP3PBOX {distance} iso\n"
        
        if self.ions:
            for ion, count in self.ions.items():
                if self.ions_rand:
                    tleap_lines += f"addionsrand mol {ion} {count}\n"
                else:
                    tleap_lines += f"addions mol {ion} {count}\n"
        
        if self.box_size:
            x, y, z = self.box_size
            tleap_lines += 'set mol box {'+f'{x} {y} {z}'+'}\n'
        
        if self.no_centre:
            tleap_lines += 'set default nocenter on\n'
        
        if self.save_protein:
            tleap_lines += f"savepdb mol {pdb_out}\n"
        
        tleap_lines += f"logfile {parm7_out.replace('parm7', 'tleap.log')}\n"
        tleap_lines += f"saveamberparm mol {parm7_out} {rst7_out}\nquit"
        print(f'Running Tleap with input:\n{tleap_lines}\n')
        run_tleap(tleap_lines)

class PackmolInput:
    '''
    Packmol Input object
    '''
    def __init__(
            self,
            n_cosolvents: int = 100,
            n_waters: int = None,
            seed: int = -1,
            distance: float = 9.0,
            box_size: float = 100.0,
            tolerance: float = 2.0,
    ):
        '''
        
        Parameters
        ----------
        n_cosolvents : int, optional
            Number of cosolvent molecules to add. The default is 100.
        n_waters : int, optional
            Number of water molecules to add. The default is None.
        seed : int, optional
            Random seed for adding cosolvent molecules. The default is -1.
        sphere_size : float, optional
            Maximum distance from protein to add cosolvents
            (only if protein present). The default is 9.0.
        box_size : float, optional
            Size of box to which cosolvents should be added
            (only if protein is not present). The default is 100.0.
        tolerance : float, optional
            Minimum distance between pairs of atoms of different molecules. 
            The default is 2.0.

        '''
        
        self.n_cosolvents = n_cosolvents
        self.n_waters = n_waters
        self.seed = seed
        self.distance = distance
        
        if type(box_size) is int:
            box_size = float(box_size)
            
        if type(box_size) is float:    
            self.box_size = [box_size, box_size, box_size]
        elif type(box_size) is list:
            if len(box_size) != 3:
                raise Exception('Please provide either 1 number or list of 3'+
                                ' numbers for box size')
            else:
                self.box_size = [float(x) for x in box_size]
        else:
            raise Exception('Please provide either 1 number or list of 3'+
                            ' numbers for box size')            
        
        self.tolerance = tolerance

    def run(self, cosolvent_pdb, pdb_out, protein_pdb=None):

        packmol_lines = (f"tolerance {self.tolerance}\n"
                         "filetype pdb\n"
                         f"output {pdb_out}\n")
        
        # If a protein pdb file is provided, place the protein at the origin
        if not protein_pdb is None:
            packmol_lines += (f"structure {protein_pdb}\n"
                              f"  seed 0\n"
                              "  number 1\n"
                              "  center\n"
                              "  fixed 0. 0. 0. 0. 0. 0.\n"
                              "  add_amber_ter\n"
                              "end structure\n")
            
            sphere_size = (get_max_distance(protein_pdb)/2) + 9
            
            packmol_lines += (f"structure {cosolvent_pdb}\n"
                              f"  seed {self.seed}\n"
                              f"  number {self.n_cosolvents}\n"
                              f"  inside sphere 0. 0. 0. {sphere_size}\n"
                              "   resnumbers 2\n"
                              "   add_amber_ter\n"
                              "end structure\n")            
        # If no protein pdb file provided, just add cosolvent molecules
        else:
            water = os.path.join(cosolvents_dir.__path__._path[0], 'water.pdb')

            x, y, z = self.box_size
            if self.n_waters is not None:
                packmol_lines += (f'structure {water} \n'
                                  f'  number {self.n_waters} \n'
                                  f'  inside box 0. 0. 0. {x} {y} {z} \n'
                                  "   add_amber_ter\n"
                                  'end structure\n')
                
            packmol_lines += (f'structure {cosolvent_pdb}\n'
                           f'  number {self.n_cosolvents}\n'
                           f'  inside box 0. 0. 0. {x} {y} {z} \n'
                           "   add_amber_ter\n"
                           'end structure\n')
        print(f'Running Packmol with the input:\n{packmol_lines}\n')
        run_packmol(packmol_lines)

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

def run_parmed(parm7, HMRparm7):


    if os.path.exists(f"{HMRparm7}"):
        os.remove(f"{HMRparm7}")

    parmed_inp = tempfile.NamedTemporaryFile(mode="w",
                                             delete=False,
                                             prefix="parmed-",
                                             suffix=".inp")
    parmed_inp.write(
        f"parm {parm7}\nHMassRepartition\noutparm {HMRparm7}\nquit\n"
    )
    parmed_inp.close()

    process = Popen(
        ["parmed < {}".format(parmed_inp.name)],
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        universal_newlines=True,
        shell=True,
    )
    out, err = process.communicate()

    os.remove(parmed_inp.name)
    print(out, err)
    return out

def run_tleap(tleap_lines):

    tleap_inp = tempfile.NamedTemporaryFile(mode="w",
                                            delete=False,
                                            prefix="tleap-",
                                            suffix=".inp")
    tleap_inp.write(tleap_lines)
    tleap_inp.close()

    p = Popen(
        ["tleap -s -f {}".format(tleap_inp.name)],
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        universal_newlines=True,
        shell=True,
    )
    out, err = p.communicate()
    print(out, err)
    os.remove(tleap_inp.name)
    
    return out


def run_packmol(packmol_lines):
    packmol_inp = tempfile.NamedTemporaryFile(mode="w",
                                              delete=False,
                                              prefix="packmol-",
                                              suffix=".inp")
    packmol_inp.write(packmol_lines)
    packmol_inp.close()

    p = Popen(
        ["packmol < {}".format(packmol_inp.name)],
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        universal_newlines=True,
        shell=True,
    )
    
    out, err = p.communicate()
    
    print(out, err)
    
    os.remove(packmol_inp.name)
