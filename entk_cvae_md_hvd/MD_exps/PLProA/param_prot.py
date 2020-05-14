import os 
import sys 
import argparse 

sys.path.append('..') 
from comp_sim.param import ParameterizeAMBER_prot
from comp_sim.utils import to_pdb
from comp_sim.sim import simulate_explicit

#pdb = os.path.abspath('./lig.pdb')
pro_pdb = os.path.abspath('./PLOPro_A.pdb') 
params = ParameterizeAMBER_prot(
    pro_pdb)

print('Simulating now')


simulate_explicit(
        params['inpcrd_file'],
        params['top_file'],
        output_cm='output.h5',
        temperature=310)
