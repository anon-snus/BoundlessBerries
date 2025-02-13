import os

delay = {'from':1000, 'to':1500}

base_rpc = None # оставить так если хотите использовать дефолтную рпс



current_directory = os.getcwd()
ABIS_DIR = os.path.join(current_directory, 'data', 'abis')