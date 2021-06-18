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

def example_1():
    p = ProteinExperiment('CTB.pdb')
    p.make_system()
    p.add_minimisation_step()
    p.add_equilibration_step()
    p.add_production_step()
    #p.run()

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

example_2()