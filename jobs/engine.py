#!/usr/bin/env python3
"""
Thin entry point delegating to engine.cli.
Preserves backward compatibility with existing automation scripts and workflows.
"""
import sys
from pathlib import Path

# Ensure repo root is on sys.path so engine can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine.cli import main

if __name__ == "__main__":
    main()
