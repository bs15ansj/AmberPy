#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  1 16:27:42 2020

@author: bs15ansj
"""
import tempfile
from subprocess import PIPE, Popen
import os

amino_acids = [
     "ALA",
     "ARG",
     "ASN",
     "ASP",
     "CYS",
     "GLN",
     "GLU",
     "GLY",
     "HID",
     "HIE",
     "HIP",
     "ILE",
     "LEU",
     "LYS",
     "MET",
     "PHE",
     "PRO",
     "SER",
     "THR",
     "TRP",
     "TYR",
     "VAL",
     ]

for amino_acid in amino_acids:
    lines = "source leaprc.protein.ff14SB\n"
    lines += "mol = sequence {ACE" + f" {amino_acid} " + "NME}\n"
    lines += f"savepdb mol {amino_acid}.pdb\n"
    lines += "quit\n"

    tleap_inp = tempfile.NamedTemporaryFile(mode="w",
                                            delete=False,
                                            prefix="tleap-",
                                            suffix=".inp")
    tleap_inp.write(lines)
    tleap_inp.close()

    p = Popen(
        ["tleap -s -f {}".format(tleap_inp.name)],
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        universal_newlines=True,
        shell=True,
    )
    out, err = p.communicate()
    
    print(out)
    
    os.remove(tleap_inp.name)