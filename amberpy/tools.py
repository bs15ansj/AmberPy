#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 18:04:32 2021

@author: bs15ansj
"""
import numpy as np
import math
import os
from Bio.PDB import *
from sklearn.metrics.pairwise import euclidean_distances
import warnings
import os
from parmed.tools import netCharge
from parmed.amber import AmberParm

warnings.simplefilter('ignore')    

def get_amber_residue_names(lib_files=['aminoct12.lib', 'aminont12.lib','amino19.lib',
                                       'atomic_ions.lib', 'atomic_ions.lib']):
    
    names = []
    
    for file in lib_files:
        lines = open(os.path.join(os.environ['AMBERHOME'], 'dat/leap/lib', file), 'r').readlines()
        for line in lines[1:]:
            if not line.startswith('!'):
                names.append(line.strip().replace('"', ''))
            else:
                break
    
    names.append('HIS')
    
    return names      
            

def count_waters(pdb):
    lines = open(pdb, 'r').readlines()
    
    lines = [line for line in lines if line.startswith('ATOM')]
    
    resnames = [line[17:20] for line in lines]
    waters = int(resnames.count('WAT')/3)
    return waters

def get_box_dimensions(pdb):
    lines = open(pdb, 'r').readlines()
    
    for line in lines:
        if line.startswith('CRYST'):
            x = line[8:15]
            y = line[17:24]
            z = line[26:33]
            
    return [float(x), float(y), float(z)]

def get_protein_termini(pdb):
    
    protein_residue_names = get_amber_residue_names(lib_files=['aminoct12.lib', 'aminont12.lib','amino19.lib'])
    
    parser = PDBParser()
    structure = parser.get_structure('tmp', pdb)

    protein_residues = [residue for residue in structure.get_residues() if residue.resname in protein_residue_names]
    tleap_indices = list(range(1, len(list(protein_residues))+1))
    pdb_to_tleap = {(residue._id[1], residue.full_id[2]) : tleap_indices[i] for i, residue in enumerate(protein_residues)}
    
    indices = []
    for chain in structure.get_chains():
        chain_indices = []
        for residue in chain:
            
            if residue.resname in protein_residue_names:

                chain_indices.append(pdb_to_tleap[(residue._id[1], residue.full_id[2])])
        indices.append(chain_indices)
    
    ranges = []
 
    for index_range in indices:
        if len(index_range) == (index_range[-1] + 1 - index_range[0]):
            ranges.append((index_range[0], index_range[-1]))
        
        else:
            splits = []
            for i, index in enumerate(index_range[:-1]):
                if index_range[i+1] - index == 1:
                    pass
                else:
                    splits.append(i+1)
    
    return ranges


def translate(pdb, centre):
    
    '''    
    Translate pdb file to centre = [x, y, z]
    '''
    
    parser = PDBParser()
    structure = parser.get_structure('tmp', pdb)

    coords = []
    for atom in structure.get_atoms():
        coords.append(atom.get_coord())
        
    com = np.mean(coords, axis=0)
    
    for atom in structure.get_atoms():
        atom.set_coord(atom.get_coord() - com + np.array(centre))
    
    io = PDBIO()
    io.set_structure(structure)
    io.save('tmp.pdb')
    os.system(f'rm {pdb}')
    os.rename('tmp.pdb', pdb)
                    
def get_max_distance(pdb, residues=None):
    
    '''
    Get the maximum euclidean distance between any two points in a pdb file. 
    '''
    
    parser = PDBParser()
    structure = parser.get_structure('tmp', pdb)
    if residues is None:
        atoms = structure.get_atoms()
    elif type(residues) is tuple:
        atoms = []
        for res in structure.get_residues():
            if residues[0] <= res.get_id()[1] <= residues[1]:
                for atom in res.get_atoms():
                    atoms.append(atom)
    coords = np.array([atom.get_coord() for atom in atoms])
    return np.max(euclidean_distances(coords,coords))

def get_charge(parm):
    
    parm = AmberParm(parm)
    action = netCharge(parm)
    charge = action.execute()
    if charge > 0:
        return math.floor(charge)
    elif charge < 0:
        return math.ceil(charge)
    else:
        return 0
    
def strip(pdb, stripped_pdb, residues=['WAT']):
    '''
    Strips water molecules from PDB.
    '''
    lines = open(pdb, 'r').readlines()
    
    with open(stripped_pdb, 'w+') as f:
        for line in lines:
            if not [res for res in residues if(res in line)]:
                f.write(line)
      
    
def count_atoms(cosolvent):
    
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure(cosolvent, f'/home/bs15ansj/AmberPy/amberpy/cosolvents/amino_acids/{cosolvent}.pdb')
    
    return len(list(structure.get_atoms()))
    










