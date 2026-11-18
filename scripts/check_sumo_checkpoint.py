#!/usr/bin/env python3
"""Compatibility entry point; implementation lives in autonomous_traffic."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from autonomous_traffic.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["checkpoint-probe", *sys.argv[1:]]))
