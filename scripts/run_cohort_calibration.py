"""Canonical module entry keeps saved research model class names portable."""
from pathlib import Path
import sys,argparse
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ml import cohort_calibration

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','fit','evaluate','verify'])
    getattr(cohort_calibration,p.parse_args().stage)()
