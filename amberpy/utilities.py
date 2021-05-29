#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 26
@author: bs15ansj

This module contains simple utlility functions used by other modules of 
amberpy.

get_name_from_file(file)
    This function returns a name based on an input file. The name is the 
    basename of the file without the suffix. If the file is None, None will 
    be returned.
    
get_name_from_input_list(input_list)
    Given a list of inputs (which may be names or file names), this function 
    returns the inputs as a string containing the names of the inputs separated
    by '.'. If any of the inputs are None, these are not included in the 
    returned name string.

"""
import os

def get_name_from_file(file):
    '''
    This function returns a name based on an input file. The name is the 
    basename of the file without the suffix. If the file is None, None will 
    be returned.   
    '''
    try:
        return '.'.join(os.path.basename(file).split('.')[:-1])
    except:
        return None

def get_name_from_input_list(input_list):
    '''
    Given a list of inputs (which may be names or file names), this function 
    returns the inputs as a string containing the names of the inputs separated
    by '.'. If any of the inputs are None, these are not included in the 
    returned name string.
    '''
    return '.'.join(filter(None.__ne__,[get_name_from_file(file) if get_name_from_file(file) != '' else file for file in input_list]))