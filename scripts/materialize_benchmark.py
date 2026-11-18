#!/usr/bin/env python3
"""Compatibility entry point; implementation lives in autonomous_traffic."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from autonomous_traffic.cli import main
from autonomous_traffic.demand import largest_remainder as largest_remainder
from autonomous_traffic.demand import materialize as materialize
from autonomous_traffic.outputs import write_outputs as write_outputs
from autonomous_traffic.randomness import random_stream as random_stream

if __name__ == "__main__":
    raise SystemExit(main(["materialize", *sys.argv[1:]]))
