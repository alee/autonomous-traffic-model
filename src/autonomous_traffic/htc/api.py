"""CLI registration for non-submitting HTC preparation and headless workers."""

import json
from pathlib import Path


def add_commands(sub):
    demo = sub.add_parser(
        "htc-demo",
        help="Create synthetic inputs for local batch validation, not Phoenix data",
    )
    demo.add_argument("--output", type=Path, required=True)
    demo.add_argument("--netgenerate")
    plan = sub.add_parser(
        "htc-plan",
        help="Freeze prepared parameter cases and render an HTCondor batch without submitting",
    )
    plan.add_argument("--sweep", type=Path, required=True)
    plan.add_argument("--output", type=Path, required=True)
    plan.add_argument(
        "--sif",
        type=Path,
        help="Local SIF to checksum and stage for Apptainer execution by HTCondor",
    )
    plan.add_argument(
        "--image",
        help="Immutable docker://registry/image@sha256:digest or osdf:///.../worker-<sha256>.sif; omit for a non-submitting template",
    )
    pre = sub.add_parser(
        "htc-preflight",
        help="Check transferred inputs; run condor_submit -dry-run only when available",
    )
    pre.add_argument("--batch", type=Path, required=True)
    run = sub.add_parser(
        "htc-run",
        help="Execute one immutable headless task locally or in a worker container",
    )
    run.add_argument("--task", type=Path, required=True)
    run.add_argument("--bundle", type=Path, required=True)
    run.add_argument("--output", type=Path, required=True)
    run.add_argument("--sumo")
    local = sub.add_parser(
        "htc-local",
        help="Debug a prepared batch locally with isolated independent native workers",
    )
    local.add_argument("--batch", type=Path, required=True)
    local.add_argument("--jobs", type=int, default=1)
    local.add_argument("--sumo")
    collect = sub.add_parser(
        "htc-collect",
        help="Validate returned result identities and report missing/failed tasks",
    )
    collect.add_argument("--batch", type=Path, required=True)
    collect.add_argument("--output", type=Path, required=True)


def dispatch(args):
    code = 0
    if args.command == "htc-demo":
        from .demo import create_demo

        result = create_demo(args.output, args.netgenerate)
    elif args.command == "htc-plan":
        from .plan import prepare

        result = prepare(args.sweep, args.output, args.image, args.sif)
        result = {k: v for k, v in result.items() if k != "tasks"}
    elif args.command == "htc-preflight":
        from .plan import preflight

        result = preflight(args.batch)
    elif args.command == "htc-local":
        from .local import run_local

        result = run_local(args.batch, args.jobs, args.sumo)
        code = 0 if result["failed"] == 0 else 2
    elif args.command == "htc-run":
        from .worker import run_task

        result, code = run_task(args.task, args.bundle, args.output, args.sumo)
    else:
        from .collect import collect

        result = collect(args.batch, args.output)
        code = 0 if result["complete"] else 2
    print(json.dumps(result, indent=2, allow_nan=False))
    return code
