#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 29 20:10:36 2021

@author: bs15ansj
"""
import os

remoteworkdir = ""

# If no remoteworkdir set, assume that it is a directory with the same username
# as the user on /nobackup
if remoteworkdir == "":
    username = os.path.basename(os.path.expanduser("~"))
    remoteworkdir = os.path.join('/nobackup', username)