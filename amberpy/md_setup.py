#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  5 11:12:13 2020

@author: bs15ansj
"""

import tempfile
from subprocess import PIPE, Popen
import os
import shutil

from amberpy.tools import get_max_distance
from amberpy.utilities import get_name_from_input_list
import amberpy.cosolvents as cosolvents_dir
from amberpy.cosolvents import COSOLVENTS
import logging


logger = logging.getLogger(__name__)

class TleapInput:
    '''
    Tleap Input object
    '''
    def __init__(self, 
                 protein_forcefield: str = "ff19SB", 
                 water_forcefield: str = "tip3p",
                 solvate: bool = True,
                 shape: str = "box", distance: float = 12.0, 
                 distance_from_residues: tuple = None, 
                 ions: dict = {"Na+": 0, "Cl-": 0},
                 save_protein: bool = True,
                 ions_rand: bool = False,
                 box_size: float = None,
                 no_centre: bool = False,
                 frcmod_list=None,
                 mol2_dict=None,
                 iso=True):
        
        self.protein_forcefield = protein_forcefield
        self.water_forcefield = water_forcefield
        self.solvate = solvate
        self.distance = distance
        self.distance_from_residues = distance_from_residues
        self.ions = ions
        self.save_protein = save_protein
        self.shape = shape
        self.ions_rand = ions_rand
        self.frcmod_list = frcmod_list
        self.mol2_dict = mol2_dict
        self.iso = iso
        
        if box_size is not None:
            if type(box_size) is int:
                box_size = float(box_size)
                
            if type(box_size) is float:    
                self.box_size = [box_size, box_size, box_size]
            elif type(box_size) is list:
                if len(box_size) != 3:
                    raise Exception('Please provide either 1 number or list of 3'+
                                    ' numbers for box size')
                else:
                    self.box_size = [float(x) for x in box_size]
            else:
                raise Exception('Please provide either 1 number or list of 3'+
                                ' numbers for box size')
        else:
            self.box_size = None
            
        self.no_centre = no_centre
        
    def run(
            self,
            pdb,
            parm7_out,
            rst7_out,
            pdb_out=None
    ):
        
        
        tleap_lines = f"source leaprc.protein.{self.protein_forcefield}\n"

        if self.solvate or self.box_size:
            tleap_lines += f"source leaprc.water.{self.water_forcefield}\n"
        
        if not self.frcmod_list is None:
            for frcmod in self.frcmod_list:
                if not frcmod is None:
                    tleap_lines += f"loadamberparams {frcmod}\n"
        
        if not self.mol2_dict is None:
            for name, mol2 in self.mol2_dict.items():
                if not mol2 is None:
                    tleap_lines += f"{name} = loadmol2 {mol2}\n"
            
        if not pdb is None:
            tleap_lines += f"mol = loadpdb {pdb}\n"

        if self.solvate:
            distance = self.distance
                
            if self.distance_from_residues:
                start, stop, distance = self.distance_from_residues
                d1 = get_max_distance(pdb, residues=(start, stop))
                d2 = get_max_distance(pdb)
                distance -= (d2 - d1)/2
            
            logger.info(f'Solvating system with a water box {distance} '
                        'Angstroms from residues.')
            
            if self.iso:
                tleap_lines += f"solvate{self.shape} mol TIP3PBOX {distance} iso\n"
            else:
                tleap_lines += f"solvate{self.shape} mol TIP3PBOX {distance}\n"
        
            if self.ions:
                logger.info(f'Adding ions from dictionary: {self.ions}')
                for ion, count in self.ions.items():
                    if self.ions_rand:
                        tleap_lines += f"addionsrand mol {ion} {count}\n"
                    else:
                        tleap_lines += f"addions mol {ion} {count}\n"
        
        if self.box_size:
            x, y, z = self.box_size
            tleap_lines += 'set mol box {'+f'{x} {y} {z}'+'}\n'
        
        if self.no_centre:
            tleap_lines += 'set default nocenter on\n'
        
        if self.save_protein:
            tleap_lines += f"savepdb mol {pdb_out}\n"
        
        tleap_lines += f"saveamberparm mol {parm7_out} {rst7_out}\nquit"
        run_tleap(tleap_lines)
        
        logger.info(f"Saving tleap output to '{parm7_out}' and '{rst7_out}'")
        logger.info("Tleap log file saved to 'leap.log'")
        
class PackmolInput:
    '''
    Packmol Input object
    '''
    def __init__(
            self,
            box_size: float = 100.0,
            tolerance: float = 2.0,
        ):
        '''
        
        Parameters
        ----------
        seed : int, optional
            Random seed for adding cosolvent molecules. The default is -1.
        box_size : float, optional
            Size of box to which cosolvents should be added
            (only if protein is not present). The default is 100.0.
        tolerance : float, optional
            Minimum distance between pairs of atoms of different molecules. 
            The default is 2.0.

        '''
        
        # Set attributes
        self._check_valid_box_size(box_size)        
        self.tolerance = tolerance
        self.packmol_lines = ''

        # Annoyling, packmol won't work if the path to the input files go over
        # the allowed number of columns. To minimise the chance of 
        # the file paths being to long, each input pdb file (apart from the 
        # protein is added to a list of pdb files so that the run method
        # can copy the files to the current directory whilst running, then 
        # delete them afterwards.
        self.remove_files = []
        self.water_pdb = os.path.join(cosolvents_dir.__path__[0], 
                                           'water.pdb')
                                        
        
    def add_protein(self, protein_pdb, seed=0):
        
        '''
        Adds add a protein to the centre of the box. 
        '''

        self.packmol_lines += (f"structure {protein_pdb}\n"
                               f"   seed {seed}\n"
                                "   number 1\n"
                                "   center\n"
                                "   fixed 0. 0. 0. 0. 0. 0.\n"
                                "   add_amber_ter\n"
                                "end structure\n")

    def add_cosolvent(self, cosolvent, n_cosolvents, outside_sphere=None):

        '''
        Adds cosolvents to the box. 
        ''' 

        cosolvent_pdb = self._get_cosolvent_pdb(cosolvent)
        self._copy_and_queue_removal(cosolvent_pdb, f"{cosolvent}.pdb")

        x, y, z = self.box_size

        self.packmol_lines += (f"structure {cosolvent}.pdb\n"
                                "   resnumbers 2\n"
                               f"   number {n_cosolvents}\n"
                               f"   inside box {0-(x/2)} {0-(y/2)} {0-(z/2)} {0+(x/2)} {0+(y/2)} {0+(z/2)}\n"
                                "   add_amber_ter\n"
                                "end structure\n")

    def add_waters(self, n_waters):

        '''
        Adds waters to the box.
        '''

        self._copy_and_queue_removal(self.water_pdb, "water.pdb")

        x, y, z = self.box_size
        
        self.packmol_lines += (f"structure water.pdb\n"
                                "   resnumbers 2\n"
                               f"   number {n_waters}\n"
                               f"   inside box {0-(x/2)} {0-(y/2)} {0-(z/2)} {0+(x/2)} {0+(y/2)} {0+(z/2)}\n"
                                "   add_amber_ter\n"
                                "end structure\n")    

    def add_ions(self, ions):

        '''
        Adds ions to the box.
        '''

        x, y, z = self.box_size

        if type(ions) is dict:
            for ion, n_ions in ions.items():
                if type(n_ions) is int:

                    ion_pdb = self._get_ion_pdb(ion)
                    self._copy_and_queue_removal(ion_pdb, f'{ion}.pdb')

                    self.packmol_lines += (f"structure {ion}.pdb\n"
                                            "   resnumbers 2\n"
                                           f"   number {n_ions}\n"
                                           f"   inside box {0-(x/2)} {0-(y/2)} {0-(z/2)} {0+(x/2)} {0+(y/2)} {0+(z/2)}\n"
                                            "   add_amber_ter\n"
                                            "end structure\n") 

                else:
                    raise Exception('Number of ions must be an integer.')

        else:
            raise Exception('Ions must be a dictionary containing ion names as ' +
                            'keys and number of ions as values.')

    def run(self, pdb_out):

        self.packmol_lines = (f"tolerance {self.tolerance}\n"
                               "filetype pdb\n"
                              f"output {pdb_out}\n") + self.packmol_lines

        run_packmol(self.packmol_lines)

        logger.info(f"Saving system as '{pdb_out}'")
        
        for f in self.remove_files:
            os.remove(f)

    def _check_valid_box_size(self, box_size):
        
        '''
        Function to check box size argument is valid. If it is, it is set as
        the box_size attribute.
        '''
        
        if type(box_size) is int:
            box_size = float(box_size)
            
        if type(box_size) is float:    
            self.box_size = [box_size, box_size, box_size]
        elif type(box_size) is list:
            if len(box_size) != 3:
                raise Exception('Please provide either 1 number or list of 3'+
                                ' numbers for box size')
            else:
                self.box_size = [float(x) for x in box_size]
        else:
            raise Exception('Please provide either 1 number or list of 3'+
                            ' numbers for box size')
            
    def _check_valide_outside_sphere(self, outside_sphere):

        '''
        Function to check outside_sphere argument is valid. If it is, it is 
        returned as a list of floats.
        '''
        
        if outside_sphere is not None:
            if type(outside_sphere) is int:
                outside_sphere = float(outside_sphere)
                
            if type(outside_sphere) is float:    
                return [outside_sphere, outside_sphere, outside_sphere]
            elif type(outside_sphere) is list:
                if len(outside_sphere) != 3:
                    raise Exception('Please provide either 1 number or list of 3'+
                                    ' numbers for outside_sphere')
                else:
                    return [float(x) for x in outside_sphere]
            else:
                raise Exception('Please provide either 1 number or list of 3'+
                                ' numbers for outside_sphere')

    def _get_cosolvent_pdb(self, cosolvent):

        # Check cosolvent is available
        if cosolvent not in COSOLVENTS.keys():
            raise Exception(f'{cosolvent} not in cosolvent directory')

        # Get cosolvent pdb file name
        cosolvent_pdb = COSOLVENTS[cosolvent][1]

        return cosolvent_pdb

    def _get_ion_pdb(self, ion):

        # Check ion is available
        if not os.path.isfile(os.path.join(cosolvents_dir.__path__[0], f'{ion}.pdb')):
            raise Exception(f'{ion} is not available. Please add a pdb file for this' +
                             'ion to the amberpy/cosolvents directory.')
        else:
            return os.path.join(cosolvents_dir.__path__[0], f'{ion}.pdb')

    def _copy_and_queue_removal(self, old, new):

        shutil.copy(old, new)
        self.remove_files.append(new)

class Setup:
    
    def __init__(
        self, 
        name, 
        protein_pdb=None, 
        cosolvents=None, 
        directory=os.getcwd()
        ):
        
        # Define list of valid inputs. If adding new inputs to the class, place 
        # them in here
        input_list = [protein_pdb, cosolvents]
        if all(inp is None for inp in input_list):
            raise Exception('No valid inputs provided')
        if not type(cosolvents) is list:
            raise Exception('Cosolvents must be a list')
        
        # If no name given, generate the name from the input files
        if name is None and len(cosolvents) == 1:
            self.name = get_name_from_input_list([protein_pdb, cosolvents[0]])
        elif name is None and cosolvent_list is not None:
            logger.error('Multilple cosolvents are used in setup. Please name'+
                         ' explicitly.')
        
        # Set protein_pdb attribute even if it is None so that we can let 
        # PackmolInput handle whether or not there is a protein
        self.protein_pdb = protein_pdb
            
        if cosolvents is not None:   
            if type(cosolvents) is list:
                self._check_cosolvents(cosolvents)
            
        self.directory = directory
        
        self.parm7 = os.path.join(self.directory, self.name) + '.parm7'
        self.rst7 = os.path.join(self.directory, self.name) + '.rst7'  
        self.tleap_pdb = os.path.join(self.directory, self.name) + '.tleap.pdb' 
        
    def run_packmol(self,
                    n_waters = None, 
                    n_cosolvents = 100, 
                    box_size = [50,50,50],
                    ions = None,
                    packmol_input = None):
        
        if packmol_input is None:
            
            if box_size is None:
                raise Exception('Please provide a box size')
            
            packmol = PackmolInput(box_size=box_size)
            packmol.add_protein(self.protein_pdb)
            for cosolvent in self.cosolvents:
                packmol.add_cosolvent(cosolvent, n_cosolvents)
            if ions is not None:
                packmol.add_ions(ions)
            if n_waters is not None:
                packmol.add_waters(n_waters)
            
        elif isinstance(packmol_input, PackmolInput):
            packmol = packmol_input
            
        else:
            raise Exception('packmol_input must be an instance of the PackmolInput class or None')
        
        packmol.run(self.packmol_pdb)

    def run_tleap(self,
                  box_distance: float = 12.0,
                  box_shape: str = 'box',
                  ions: dict = {'Na+': 0, 'Cl-':0},
                  tleap_input: TleapInput = None):

        '''
        Solvates the pdb file and creates paramater/topology and coordinate 
        files for simulation.
        
        Parameters
        ----------
        box_distance : float
            Minimum distance between the protein and the edge of the water box.
        box_shape : str
            Shape of the simulation box. Choose from either 'box' (cuboid) or 
            'oct' (truncated octahedron).
        ions : dict
            Ions to add to the system. This should be a dictionary where the 
            keys are the ions and the values are the number of ions to add. 
            A value of 0 will attempt to neutralise the system with that ion. 
        hmr : bool
            Turn on hydrogen mass repartitioning. 
        tleap_input : TleapInput
            Overrides all other arguments and instead uses a TleapInput
            instance.
        '''
        
        if tleap_input is None:
            
            kwargs = {}

            kwargs['distance'] = box_distance
            kwargs['shape'] = box_shape
            kwargs['ions'] = ions
            
            tleap = TleapInput(**kwargs)
        
        else:
            tleap = tleap_input
            
        #else:
         #   print(type(tleap_input))
          #  raise Exception('tleap_input must be an instance of the TleapInput class or None')
        
        if hasattr(self, 'packmol_pdb'):
            tleap.run(self.packmol_pdb, self.parm7, self.rst7, self.tleap_pdb)
        else:
            tleap.run(self.protein_pdb, self.parm7, self.rst7, self.tleap_pdb)

    def run_parmed(self):

        self.hmr = True
        hmr_parm7 = self.parm7.replace('.parm7', '.HMR.parm7')
        run_parmed(self.parm7, hmr_parm7)
        self.parm7 = hmr_parm7
        
    def _check_cosolvents(self, cosolvents):
        
        self.cosolvents = []
        self.frcmod_list =[]
        self.mol2_dict = {}
        for cosolvent in cosolvents:
            # Check cosolvent is available
            if cosolvent not in COSOLVENTS.keys():
                raise Exception(f'{cosolvent} not in cosolvent directory')
            self.cosolvents.append(cosolvent)
            # Get cosolvent type from COSOLVENTS dict
            cosolvent_type = COSOLVENTS[cosolvent][0]
            # If cosolvent is a small molecule, add an frcmod and mol2 file
            if cosolvent_type == 'small_molecules':
                cosolvent_mol2 = COSOLVENTS[cosolvent][2]
                cosolvent_frcmod = COSOLVENTS[cosolvent][3]
                self.frcmod_list.append(cosolvent_frcmod)
                self.mol2_dict[os.path.basename(cosolvent_mol2).split('.')[0]] = cosolvent_mol2
                
        self.packmol_pdb = os.path.join(self.directory, self.name) + '.packmol.pdb'

def run_parmed(parm7, HMRparm7):

    logger.info("Running parmed.")
    logger.debug(f"Repartitioning the mass of hydrogens in '{parm7}' and "
                 f"saving to '{HMRparm7}'")

    if os.path.exists(f"{HMRparm7}"):
        os.remove(f"{HMRparm7}")

    parmed_inp = tempfile.NamedTemporaryFile(mode="w",
                                             delete=False,
                                             prefix="parmed-",
                                             suffix=".inp")
    parmed_inp.write(
        f"parm {parm7}\nHMassRepartition\noutparm {HMRparm7}\nquit\n"
    )
    parmed_inp.close()

    p = Popen(
        ["parmed < {}".format(parmed_inp.name)],
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        universal_newlines=True,
        shell=True,
    )
    
    out, err = p.communicate()
    os.remove(parmed_inp.name)
    
    if 'ERROR' in out:
        out = out.replace('\n', '\n\t')
        logger.error(f'Parmed failed, see output:\n\t{out}')
        exit()
        
    else:
        logger.info('Parmed completed succeffully.')
    return out

def run_tleap(tleap_lines):

    logger.info("Running tleap.")
    log_lines = tleap_lines.replace('\n', '\n\t')
    logger.debug(f"Tleap input lines:\n\t{log_lines}")

    tleap_inp = tempfile.NamedTemporaryFile(mode="w",
                                            delete=False,
                                            prefix="tleap-",
                                            suffix=".inp")
    tleap_inp.write(tleap_lines)
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
    os.remove(tleap_inp.name)
    
    if 'Fatal Error' in out:
        
        # Get error message from tleap
        error = out[out.find("Fatal Error!")+13:]
        error = error.replace('\n', '\n\t')
        logger.error(f"Error raised by tleap:\n\t{error}")
        exit()
        
    else:
        
        # Find any tleap warnings
        try:
            warnings = int(out[out.find('Warnings = ')+11:out.find('; Notes = ')])
        except:
            warnings = 0
        logger.info(f'Tleap completed successfully with {warnings} warnings.'
                    ' Check the tleap logfile for more info.')
            
    
    
    return out


def run_packmol(packmol_lines):
    
    logger.info("Running packmol.")
    log_lines = packmol_lines.replace('\n', '\n\t')
    logger.debug(f"Packmol input lines:\n\t{log_lines}")

    packmol_inp = tempfile.NamedTemporaryFile(mode="w",
                                              delete=False,
                                              prefix="packmol-",
                                              suffix=".inp")
    packmol_inp.write(packmol_lines)
    packmol_inp.close()

    p = Popen(
        ["packmol < {}".format(packmol_inp.name)],
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        universal_newlines=True,
        shell=True,
    )
    
    out, err = p.communicate()
    
    if 'ERROR' in out:
        out = out.replace('\n', '\n\t')
        logger.error(f'Packmol failed, see output:\n\t{out}')
        exit()
        
    else:
        logger.info('Packmol completed succeffully.')
    
    os.remove(packmol_inp.name)
