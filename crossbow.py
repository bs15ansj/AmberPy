#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 20 12:02:00 2021

@author: bs15ansj
"""
from longbow.entrypoints import longbow
import logging 

# Setup parameter dictionary 
parameters = {'disconnect': False, 
              'handler': 'mpirun',
              'job': '', 
              'hosts': '',
              'maxtime': '48:00', 
              'nochecks': False,
              'resource': '',
              'scheduler': 'sge',
              'sge-peflag': 'ib',
              'user': 'bs15ansj'}

def crossbow(name, 
             user,
             mdin, 
             parm7, 
             rst7,
             ref_rst7,
             gpu=True,
             cores=None, 
             hold_jid='',
             arc=3,
             remoteworkdir='',
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
        
    # Set gpu/cpu parameters
    if gpu == True:
        parameters['executable'] = 'pmemd.cuda_SPFP'
        parameters['cores'] = '0'
        parameters['modules'] = 'amber/20gpu'
        if arc == 3:
            parameters['gpu'] = 'p100'
        elif arc == 4:
            parameters['gpu'] = 'v100'
    elif cores is not None:
        parameters['executable'] = 'pmemd.MPI'
        parameters['cores'] = str(cores)
        parameters['modules'] = 'amber'

    # Select resource based on arc input
    if arc == 3:
        parameters['host'] = 'arc3'
    elif arc == 4:
        parameters['host'] = 'arc4'
    else:
        raise Exception('Arc can only be 3 or 4')
    
    # Set exectutable arguments from inputs/outputs
    parameters['executableargs'] = f'-O -i {mdin} -p {parm7} -c {rst7} -o {mdout} -r {out_rst7} -inf {mdinfo} -ref {ref_rst7} -x {nc}'
    
    # If minimisation is set to true don't save the trajectory 
    if minimisation == True:
        parameters['executableargs'] = f'-O -i {mdin} -p {parm7} -c {rst7} -o {mdout} -r {out_rst7} -inf {mdinfo} -ref {ref_rst7}'

    # Add some extra parameters
    parameters['log'] = f'{name}.log'
    parameters['hold_jid'] = hold_jid
    parameters['jobname'] = name
    parameters['upload-include'] = ', '.join([mdin, parm7, rst7, ref_rst7])
    parameters['upload-exclude'] = '*'
    parameters['download-include'] = ', '.join([mdout, mdinfo, out_rst7, nc])
    parameters['download-exclude'] = '*'
    parameters['remoteworkdir'] = remoteworkdir
    parameters['localworkdir'] = localworkdir
    parameters['user'] = user
    

    
    # Run longbow with empty jobs list and parameters
    jobs = {}
    
    longbow(jobs, parameters)