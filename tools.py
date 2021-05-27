#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 18:04:32 2021

@author: bs15ansj
"""
import numpy as np
import os
from Bio.PDB import *
from sklearn.metrics.pairwise import euclidean_distances
import warnings
warnings.simplefilter('ignore')    

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
    lines = open(pdb, 'r').readlines()
    
    lines = [line for line in lines if line.startswith('ATOM')]
    
    resids = [int(line[22:31].strip()) for line in lines if line[17:20] != 'WAT']
    
    # Check if resids are continuous
    if list(range(min(resids), max(resids)+1, 1)) == list(set(resids)):
        return min(resids), max(resids)
    
    #TODO Handle non-continuous protein sequence

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















