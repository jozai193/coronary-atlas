"""Launch the verified Python 3.11 app inside the host SDK environment."""
from pathlib import Path
import os
import subprocess
import sys

folder=Path(__file__).resolve().parent
environment=Path('/tmp/coronary-atlas-python311')
python=environment/'bin/python'
if not python.exists():
    subprocess.run([sys.executable,'-m','uv','venv','--python','3.11','--python-preference','only-managed',str(environment)],check=True)
    subprocess.run([sys.executable,'-m','uv','pip','install','--python',str(python),'-r',str(folder/'requirements-runtime.txt')],check=True)
os.execv(str(python),[str(python),str(folder/'server.py')])
