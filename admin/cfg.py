import os, sys
from os import path

SITE_DIR = path.dirname(path.abspath(__file__))
ROOT_DIR = path.dirname(SITE_DIR)
THIRD_PARTY_DIR = os.path.join(ROOT_DIR, 'third-party')

def path_config():
    for path in [THIRD_PARTY_DIR]:
        if path not in sys.path:
            sys.path.insert(0, path)

path_config()


WS_SERVER_URL = 'ws://localhost:8888/test/'
CFG_DIR = os.path.join(SITE_DIR, 'cfg')

cfg_local_file = path.join(CFG_DIR, 'admin.py')
if path.isfile(cfg_local_file):
    execfile(cfg_local_file)

