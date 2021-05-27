#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 25 14:52:52 2021

@author: bs15ansj
"""
import glob
import os

COSOLVENT_TYPES = ['small_molecules', 'amino_acids']

# Get cosolvents directory
cosolvents_dir = os.path.dirname(__file__)

# Create empty directory of available cosolvents
available_cosolvents = {}

# Iterate through cosolvent type directories
for cosolvent_type in COSOLVENT_TYPES:
    
    # Get list of all pdb files in directory
    cosolvent_pdbs = glob.glob(os.path.join(cosolvents_dir, cosolvent_type, '*.pdb'))
    
    for file in cosolvent_pdbs:
        
        name = os.path.basename(file).split('.')[0]
        
        # Get cosolvent name and add to available cosolvent list
        available_cosolvents[name] = [cosolvent_type]
        
        # Add pdb file to second element
        available_cosolvents[name].append(file)
        
        # Add mol2 to third element
        mol2 = file.replace('pdb', 'mol2')
        if os.path.isfile(mol2):
            available_cosolvents[name].append(mol2)
        else:
            available_cosolvents[name].append('na')
            
        # Add frcmod to fourth element
        frcmod = os.path.join(os.path.dirname(file), 'frcmod.' + name)
        if os.path.isfile(frcmod):
            available_cosolvents[name].append(frcmod)
        else:
            available_cosolvents[name].append('na')
            
# Check there are no duplicates in cosolvent directory
if len(available_cosolvents.keys()) != len(set(available_cosolvents.keys())):
    raise Exception('Duplicate cosolvents in directory')

# Define available cosolvents
COSOLVENTS = available_cosolvents
