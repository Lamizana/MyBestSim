"""Raccourci : `python main.py` équivaut à `python -m mybestsim`."""

import sys

from mybestsim.__main__ import main

if __name__ == "__main__":
    sys.exit(main())
