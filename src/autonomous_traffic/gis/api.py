"""CLI for bounded GIS preparation; never invoked by HTC workers."""

import json
from pathlib import Path


def add_commands(sub):
    p = sub.add_parser(
        "network-plan",
        help="Prepare explicit proposed AOI/context geometry and a bounded OSM query",
    )
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--benchmark", type=Path)
    p = sub.add_parser(
        "network-fetch",
        help="Acquire bounded public OSM roads/restrictions on a preparation machine",
    )
    p.add_argument("--plan", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p = sub.add_parser(
        "network-import",
        help="Record an already acquired OSM export and its declared query coverage",
    )
    p.add_argument("--osm", type=Path, required=True)
    p.add_argument(
        "--bbox", required=True, help="west,south,east,north WGS84 requested coverage"
    )
    p.add_argument("--source-uri", required=True)
    p.add_argument("--output", type=Path, required=True)
    p = sub.add_parser(
        "network-build",
        help="Convert a recorded OSM source and audit lane geometry/connectivity offline",
    )
    p.add_argument("--plan", type=Path, required=True)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--benchmark", type=Path)
    p.add_argument("--netconvert")


def dispatch(args):
    from .prepare import build, fetch, plan, record_source

    if args.command == "network-plan":
        result = plan(args.config, args.output, args.benchmark)
    elif args.command == "network-fetch":
        result = fetch(args.plan, args.output)
    elif args.command == "network-import":
        result = record_source(
            args.osm,
            args.output,
            [float(v) for v in args.bbox.split(",")],
            args.source_uri,
        )
    else:
        result = build(
            args.plan, args.source, args.output, args.benchmark, args.netconvert
        )
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0
