
##
# config.py
##

import os
import sys

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
if not ROOT_PATH in sys.path:
    sys.path.insert(0, ROOT_PATH)

SRC_PATH = os.path.join(ROOT_PATH, 'src')
if not SRC_PATH in sys.path:
    sys.path.insert(0, SRC_PATH)

