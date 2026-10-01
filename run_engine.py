#!/usr/bin/env python3
import sys
from pathlib import Path

# Ensure repo root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from engine.cli import main

if __name__ == "__main__":
    main()
