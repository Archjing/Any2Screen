#!/usr/bin/env python3
import runpy
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
runpy.run_module("cli", run_name="__main__")
