#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 27 21:36:58 2021

@author: bs15ansj
"""
from setuptools import setup, find_packages
import os



setup(
    name='AmberPy',
    version='0.0.1',
    liscence='MIT',
    description=('A tool for setting up and performing molecular dynamics '
                 'simulations using Amber on the University of Leeds Arc HPC'),
    author='Alex St John',
    author_email='bs15ansj@leeds.ac.uk',
    url='https://github.com/pacilab/AmberPy.git',
    packages=find_packages(include=['amberpy']),
    classifiers=[
         # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        
        'Programming Language :: Python :: 3.7',
        ],
    install_requires=['biopython',
                      'scikit-learn',
                      'Longbow @ git+https://github.com/pacilab/Longbow.git@master',
                      'pandas'
                      ],
    scripts=['amberpy/james']
)
