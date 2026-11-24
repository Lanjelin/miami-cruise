#!/usr/bin/python3
"""Full native icon decoding and process-local GTK lookup; private display only."""
import subprocess
import sys
from pathlib import Path
subprocess.run([sys.executable,str(Path(__file__).resolve().parents[1]/'previews/icons/render.py'),'--test-only'],check=True)
