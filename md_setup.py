#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  5 11:12:13 2020

@author: bs15ansj
"""
import tempfile
from subprocess import PIPE, Popen
import os
from amberpy3.tools import get_max_distance
import amberpy3.cosolvents as cosolvents_dir


class TleapInput:
    '''
    Tleap Input object
    '''
    def __init__(
            self,
            protein_forcefield: str = "ff14SB",
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

        tleap_lines += f"saveamberparm mol {parm7_out} {rst7_out}\nquit"
        print(tleap_lines)
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
        print(packmol_lines)
        run_packmol(packmol_lines)

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
