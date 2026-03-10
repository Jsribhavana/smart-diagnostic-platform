from __future__ import annotations
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def ensure_dirs():
    for d in [ROOT/"data", ROOT/"models", ROOT/"report", ROOT/"app", ROOT/"notebooks"]:
        d.mkdir(parents=True, exist_ok=True)

def default_dataset_path() -> Path:
    # Use existing dataset from the React app if present
    p = ROOT.parents[0] / "madhumeha-app" / "src" / "dataset" / "diabetes_completed_dataset.csv"
    return p