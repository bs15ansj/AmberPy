#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 25 17:59:50 2021

@author: bs15ansj
"""

from amberpy.experiments import ProteinExperiment, CosolventExperiment, ProteinCosolventExperiment
from amberpy import set_logging_level
import logging 

set_logging_level(logging.INFO)

def protein_experiment_example_1():

    '''A simple prorein experiment using all the defaults
    
    This function will solvate 'CTB.pdb' in a cubic water box with
    a minimum distance of 12 Angstroms way from the protein and add
    sodium and chloride ions to neutralise the system. Masses
    of hydrogen atoms will be repartitioned. Minimisation 
    will then be performed using 2500 steps of the steepest descent
    algorithm followed by 2500 steps of the conjugate gradient 
    algorithm before the system us equilibrated in the NVT ensemble, 
    heating the system up to 310 K for 125 picoseconds. Finally, 
    a production step of 100 ns will be performed in the NPT ensemble 
    at 310 K. The non-bonded cutoff limit for all MD steps is 9 
    Angstroms.
    '''

    p = ProteinExperiment('CTB.pdb')
    
    p.make_system()
    
    p.add_minimisation_step()
    
    p.add_equilibration_step()

    p.add_production_step()

    p.run()

def protein_experiment_example_2():

    '''A simple prorein experiment using non-default arguments

    This function will solvate 'CTB.pdb' in a truncated octahedron
    water box at a minimum distance of 10 Angstroms way from the 
    protein and add 100 magnesium and 100 chloride ions to neutralise 
    the system.  Minimisation will then be performed using 5000 steps 
    of the steepest descent algorithm followed by 2500 steps of the 
    conjugate gradient algorithm before the system us equilibrated in 
    the NVT ensemble, heating the system up to 300 K for 500 picoseconds. 
    Finally, a production step of 200 ns will be performed in the NPT 
    ensemble at 300 K. The non-bonded cutoff limit for all MD steps is 9 
    Angstroms.
    '''

    p = ProteinExperiment('CTB.pdb', name='protein_experiment_example_2')
    
    p.make_system(box_size=10.0, box_shape='oct', ions={'Mg+':100, 'Cl-':100})
    
    p.add_minimisation_step(steepest_descent_steps=5000)
    
    p.add_equilibration_step(target_temperature=300, simulation_time=500)

    p.add_production_step(target_temperature=300, simulation_time=200)

    p.run()

def protein_experiment_example_2():

    '''A simple prorein experiment using all the defaults
    
    This function will solvate 'CTB.pdb' in a cubic water box with
    a minimum distance of 12 Angstroms way from the protein and add
    sodium and chloride ions to neutralise the system. Masses
    of hydrogen atoms will be repartitioned. Minimisation 
    will then be performed using 2500 steps of the steepest descent
    algorithm followed by 2500 steps of the conjugate gradient 
    algorithm before the system us equilibrated in the NVT ensemble, 
    heating the system up to 310 K for 125 picoseconds. Finally, 
    a production step of 1000 ns will be performed in the NPT ensemble 
    at 310 K. The non-bonded cutoff limit for all MD steps is 9 
    Angstroms.
    '''

    p = ProteinExperiment('CTB.pdb')
    
    p.make_system()
    
    p.add_minimisation_step()
    
    p.add_equilibration_step()

    # A 1000 ns is too long to be performed on arc all in one go so
    # we will add 10 production steps of 100 ns
    for _ in range(10):
        p.add_production_step()

    p.run()

def example_2():
    c = CosolventExperiment('ALA')
    c.make_system()
    c.add_minimisation_step()
    c.add_equilibration_step()
    c.add_production_step()
    c.run()

def example_3():
    pc = ProteinCosolventExperiment('CTB.pdb', 'ALA')
    pc.make_system()
    pc.add_minimisation_step()
    pc.add_equilibration_step()
    pc.add_production_step()
    pc.run()

example_1()