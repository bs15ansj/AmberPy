#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 20 12:02:00 2021

@author: bs15ansj
"""
import os
from longbow.entrypoints import longbow
import logging

# Setup logger (must be done like this so that the longbow logger works)
LOG = logging.getLogger("longbow")
logformat = logging.Formatter('%(asctime)s - %(levelname)-8s - '
                              '%(name)s - %(message)s',
                              '%Y-%m-%d %H:%M:%S')
LOG.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logformat)
LOG.addHandler(handler)

# Setup parameter dictionary 
parameters = {'disconnect': False, 
              'job': '', 
              'hosts': os.path.expanduser('~/.amberpy/hosts.conf'),
              'maxtime': '48:00', 
              'nochecks': False,
              'resource': '',
              'sge-peflag': 'ib',}

def crossbow(name, 
             mdin, 
             parm7, 
             rst7,
             ref_rst7,
             gpu=True,
             cores=None, 
             hold_jid='',
             arc=3,
             localworkdir='',
             minimisation=False):
    
    # Get the output file names from the inputs
    mdout = mdin.replace('mdin', 'mdout')
    mdinfo = mdin.replace('mdin', 'mdinfo')
    out_rst7 = mdin.replace('mdin', 'rst7')
    nc = mdin.replace('mdin', 'nc')
    
    # Job names on arc cannot start with a digit, so if name does, place an 'a'
    # at the start 
    if name[0].isdigit():
        name = 'a'+name
        print(f"Arc job name can't start with digit, changing to {name}")
    
    # Ensure that only gpu OR cores have been specified
    if gpu == True and cores is not None:
        gpu = False
    elif gpu == False and cores is None:
        raise Exception("Please specify either gpu or cores")
        
    if cores is not None:
        parameters['cores'] = str(cores)
        if arc == 3:
            parameters['resource'] = 'arc3-cpu'
        elif arc == 4:
            parameters['resource'] = 'arc4-cpu'
            
    # Set gpu/cpu parameters
    elif gpu == True:
        parameters['cores'] = str(0)
        if arc == 3:
            parameters['resource'] = 'arc3-gpu'
        elif arc == 4:
            parameters['resource'] = 'arc4-gpu'

    
    # Set exectutable arguments from inputs/outputs
    parameters['executableargs'] = f'-O -i {mdin} -p {parm7} -c {rst7} -o {mdout} -r {out_rst7} -inf {mdinfo} -ref {ref_rst7} -x {nc}'
    
    # If minimisation is set to true don't save the trajectory 
    if minimisation == True:
        parameters['executableargs'] = f'-O -i {mdin} -p {parm7} -c {rst7} -o {mdout} -r {out_rst7} -inf {mdinfo} -ref {ref_rst7}'

    # Add some extra parameters
    parameters['log'] = os.path.join(localworkdir, f'{name}.log')
    parameters['hold_jid'] = hold_jid
    parameters['jobname'] = name
    parameters['upload-include'] = ', '.join([mdin, parm7, rst7, ref_rst7])
    parameters['upload-exclude'] = '*'
    parameters['download-include'] = ', '.join([mdout, mdinfo, out_rst7, nc])
    parameters['download-exclude'] = '*'
    parameters['localworkdir'] = localworkdir
    

    
    # Run longbow with empty jobs list and parameters
    jobs = {}
    
    longbow(jobs, parameters)