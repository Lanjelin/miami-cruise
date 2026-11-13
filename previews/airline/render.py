"""Render native airline; AIRLINE points to an existing plugin checkout."""
from pathlib import Path
import sys
sys.dont_write_bytecode = True
sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parents[2])]
from _plugin_capture import render
render('airline', Path(sys.argv[1]))
