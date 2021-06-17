#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 27 21:36:58 2021

@author: bs15ansj
"""
from setuptools import setup, find_packages
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='AmberPy',
    version='0.0.1',
    liscence='MIT',
    description=('A tool for setting up and performing molecular dynamics '
                 'simulations using Amber on the University of Leeds Arc HPC'),
    author='Alex St John',
    author_email='bs15ansj@leeds.ac.uk',
    url='https://github.com/pacilab/AmberPy.git',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(include=['amberpy', 'amberpy*']),
    classifiers=[
         # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        
        'Programming Language :: Python :: 3.7',
        ],
    install_requires=['biopython',
                      'scikit-learn',
                      'Longbow @ git+https://github.com/pacilab/Longbow.git@master',
                      'pandas',
                      'multiprocessing-logging'
                      ],
    scripts=['amberpy/james']
)

try:
    # Setting up the .Longbow directory.
    if not os.path.isdir(os.path.expanduser('~/.amberpy')):
        print('Making hidden AmberPy directory at "~/.amberpy"')
        os.mkdir(os.path.expanduser('~/.amberpy'))
    
    else:
        print('Directory already exists at "~/.amberpy" - Skipping')
        
        
    if not os.path.isfile(os.path.expanduser('~/.amberpy/hosts.conf')):
        print('Making configuration file at "~/.amberpy/hosts.conf"')
        username = os.getlogin()
        remoteworkdir = '/nobackup/' + os.getlogin()
        
        HOSTFILE = open(os.path.expanduser('~/.amberpy/hosts.conf'), 'w+')
    
    

        HOSTFILE.write(
                    "[arc3-gpu]\n"
                    "host = arc3\n"
                    "cores = 0\n"
                    "arcsge-gpu = p100\n"
                    "scheduler = arcsge\n"
                    "modules = amber/20gpu\n"
                    "executable = pmemd.cuda_SPFP\n"
                    f"remoteworkdir = {remoteworkdir}\n"
                    f"user = {username}\n"
                    "\n"
                    "[arc3-cpu]\n"
                    "host = arc3\n"
                    "scheduler = arcsge\n"
                    "modules = amber\n"
                    "handler = mpirun\n"
                    "executable = pmemd.MPI\n"
                    f"remoteworkdir = {remoteworkdir}\n"
                    f"user = {username}\n"
                    "\n"
                    "[arc4-gpu]\n"
                    "host = arc4\n"
                    "cores = 0\n"
                    "arcsge-gpu = v100\n"
                    "scheduler = arcsge\n"
                    "modules = amber/20gpu\n"
                    "executable = pmemd.cuda_SPFP\n"
                    f"remoteworkdir = {remoteworkdir}\n"
                    f"user = {username}\n"
                    "\n"
                    "[arc4-cpu]\n"
                    "host = arc4\n"
                    "scheduler = arcsge\n"
                    "modules = amber\n"
                    "handler = mpirun\n"
                    "executable = pmemd.MPI\n"
                    f"remoteworkdir = {remoteworkdir}\n"
                    f"user = {username}\n"
                    "\n")

        HOSTFILE.close()


    else:
        print('File already exists at "~/.amberpy/hosts.conf" - Skipping')

except IOError:

    print('AmberPy failed to create the host configuration file in '
          '"~/.amberpy/hosts.conf"')

