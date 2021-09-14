#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 20 12:02:00 2021

@author: bs15ansj
"""
import os
import glob
from longbow.entrypoints import longbow


# Setup parameter dictionary 
parameters = {'disconnect': False, 
              'job': '', 
              'hosts': os.path.expanduser('~/.amberpy/hosts.conf'),
              'maxtime': '48:00', 
              'nochecks': False,
              'resource': '',
              'sge-peflag': 'ib',}

def run_cpptraj(name, 
          cpptraj,
          nc, 
          parm7, 
          rst7,
          ref_parm7,
          ref_rst7,
          arc=3,
          localworkdir='',
          pollingfrequency=60):
    
    # Job names on arc cannot start with a digit, so if name does, place an 'a'
    # at the start 
    if name[0].isdigit():
        name = 'a'+name
        print(f"Arc job name can't start with digit, changing to {name}")

    # Remove any job output/error files 
    try:
        for f in glob.glob(os.path.join(localworkdir, f'{name}.o*')):
            os.remove(f)
    except IndexError:
        pass
    try:
        for f in glob.glob(os.path.join(localworkdir, f'{name}.e*')):
            os.remove(f)
    except IndexError:
        pass   

    parameters['cores'] = str(cores)
    if arc == 3:
        parameters['resource'] = 'arc3-cpu'
    elif arc == 4:
        parameters['resource'] = 'arc4-cpu'

    
    # Set exectutable arguments from inputs/outputs
    parameters['executableargs'] = f'cpptraj < {cpptraj}'

    # Add some extra parameters
    parameters['log'] = os.path.join(localworkdir, f'{name}.log')
    parameters['hold_jid'] = hold_jid
    parameters['jobname'] = name
    parameters['upload-include'] = ', '.join([nc, parm7, ref_parm7, rst7, ref_rst7])
    parameters['upload-exclude'] = '*'
    parameters['download-include'] = '*'
    parameters['download-exclude'] = ', '.join([nc, parm7, ref_parm7, rst7, ref_rst7])
    parameters['localworkdir'] = localworkdir
    parameters['polling-frequency'] = pollingfrequency
    
    # Run longbow with empty jobs list and parameters
    jobs = {}
    
    longbow(jobs, parameters)


def run_pmemd(name, 
          mdin, 
          parm7, 
          rst7,
          ref_rst7,
          gpu=True,
          cores=None, 
          hold_jid='',
          arc=3,
          localworkdir='',
          minimisation=False,
          pollingfrequency=60):
    
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
    

    # Remove any job output/error files 
    try:
        for f in glob.glob(os.path.join(localworkdir, f'{name}.o*')):
            os.remove(f)
    except IndexError:
        pass
    try:
        for f in glob.glob(os.path.join(localworkdir, f'{name}.e*')):
            os.remove(f)
    except IndexError:
        pass   

    
        
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
    parameters['download-include'] = ', '.join([mdout, mdinfo, out_rst7, nc, name+'.o*', name+'.e*'])
    parameters['download-exclude'] = '*'
    parameters['localworkdir'] = localworkdir
    parameters['polling-frequency'] = pollingfrequency
    
    # Run longbow with empty jobs list and parameters
    jobs = {}
    
    longbow(jobs, parameters)
    
    if box_change_error(name, localworkdir):
        return 1
    elif not cuda_error:
        return 2
    else:
        return 0
    
def box_change_error(name, localworkdir):

    for fname in glob.glob(os.path.join(localworkdir, f'{name}.o*')):
    
        with open(fname, 'r') as f:
            if 'Periodic box dimensions have changed' in f.read():
                return True
            else:
                return False

def cuda_error(name, localworkdir):

    for fname in glob.glob(os.path.join(localworkdir, f'{name}.o*')):
    
        with open(fname, 'r') as f:
            if 'cudaGetDeviceCount failed no CUDA-capable device is detected' in f.read():
                return True
            else:
                pass
        
    return False
    