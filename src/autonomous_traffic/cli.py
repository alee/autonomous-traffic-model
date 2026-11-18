"""Command-line entry points for reproducible inputs and engine checks."""

import argparse
import importlib.metadata
import json
import platform
import shutil
import sys
from pathlib import Path

from . import __version__
from .demand import materialize
from .outputs import write_outputs


def nonnegative_seed(value):
    try:
        seed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("seed must be an integer") from exc
    if seed < 0:
        raise argparse.ArgumentTypeError("seed must be nonnegative")
    return seed


def environment_report():
    packages = {}
    for name in ["eclipse-sumo", "traci", "sumolib", "sumo-data"]:
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    return {
        "package_version": __version__,
        "python": platform.python_version(),
        "sumo_binary": shutil.which("sumo"),
        "netgenerate_binary": shutil.which("netgenerate"),
        "optional_packages": packages,
        "note": "Environment inventory only; does not establish model readiness or checkpoint compatibility.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(prog="autonomous-traffic", description=__doc__)
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)
    demand = sub.add_parser(
        "materialize",
        help="Create accepted synthetic inputs without routing or simulating traffic",
    )
    demand.add_argument("--config", type=Path, required=True)
    demand.add_argument("--output", type=Path, required=True)
    demand.add_argument("--seed", type=nonnegative_seed, default=20261117)
    checkpoint = sub.add_parser(
        "checkpoint-probe",
        help="Test observed continuation on a synthetic SUMO fixture",
    )
    checkpoint.add_argument("--output", type=Path, required=True)
    checkpoint.add_argument(
        "--sumo", help="Explicit SUMO binary; otherwise search PATH"
    )
    checkpoint.add_argument(
        "--netgenerate", help="Explicit netgenerate binary; otherwise search PATH"
    )
    sub.add_parser(
        "doctor", help="Report package, Python and optional engine availability"
    )
    args = parser.parse_args(argv)
    try:
        if args.command == "doctor":
            print(json.dumps(environment_report(), indent=2))
            return 0
        if args.command == "materialize":
            raw = args.config.read_bytes()
            records = materialize(json.loads(raw), args.seed)
            write_outputs(records, args.output, raw)
            print(json.dumps(records["summary"], indent=2))
            return 0
        sumo, netgenerate = (
            args.sumo or shutil.which("sumo"),
            args.netgenerate or shutil.which("netgenerate"),
        )
        if not sumo or not netgenerate:
            parser.error(
                "checkpoint-probe requires SUMO; run 'uv sync --locked --extra sumo' or supply both binary paths"
            )
        try:
            from .sumo.probe import probe

            return probe(args.output.resolve(), sumo, netgenerate)
        except ModuleNotFoundError as exc:
            if exc.name not in {"traci", "sumolib"}:
                raise
            parser.error(
                "checkpoint-probe requires the sumo extra: uv sync --locked --extra sumo"
            )
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
