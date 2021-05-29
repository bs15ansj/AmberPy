#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 25 17:59:50 2021

@author: bs15ansj
"""

from amberpy.experiments import ProteinSimulation, CosolventSimulation, ProteinCosolventSimulation

p = ProteinSimulation('CTB.pdb')
p.make_system()
p.add_minimisation_step()
p.add_equilibration_step()
p.add_production_step()
p.run('bs15ansj', '/home/home02/bs15ansj/a/longbow/', arc=3, cores=32)
'''
c = CosolventSimulation('ALA')
c.make_system()
c.add_minimisation_step()
c.add_equilibration_step()
c.add_production_step()

pc = ProteinCosolventSimulation('CTB.pdb', 'ALA')
pc.make_system()
pc.add_minimisation_step()
pc.add_equilibration_step()
pc.add_production_step()

p.run('bs15ansj', '/home/home02/bs15ansj/a/longbow/', arc=4, cores=32)
c.run('bs15ansj', '/home/home02/bs15ansj/a/longbow/', arc=4, cores=32)
pc.run('bs15ansj', '/home/home02/bs15ansj/a/longbow/', arc=4, cores=32)
'''
