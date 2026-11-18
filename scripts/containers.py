#!/usr/bin/env python3
"""Container transport only. Model parameters and execution remain in the installed CLI.

Docker uses an anonymous volume plus docker cp, so Docker Desktop/remote daemons
need no access to the host's workspace path. Input workspaces are preserved and
each invocation exports a fresh output workspace, including on application failure.
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

SMOKE = """set -eu
autonomous-traffic doctor > environment.json
autonomous-traffic scenario-configure --base /opt/traffic/examples/coronado-benchmark.json --start-local 22:00:00 --output scenario.json
autonomous-traffic network-plan --config /opt/traffic/examples/gis/coronado-network.proposed.json --benchmark scenario.json --output geometry
autonomous-traffic htc-demo --output inputs
autonomous-traffic htc-plan --sweep inputs/sweep.json --output batch
autonomous-traffic htc-local --batch batch --jobs 2
autonomous-traffic htc-collect --batch batch --output collected
"""


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def call(args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)


def image_identity(image):
    result = call(["docker", "image", "inspect", image], capture_output=True, text=True)
    data = json.loads(result.stdout)[0]
    if data["Architecture"] != "amd64" or data["Os"] != "linux":
        raise ValueError("The initial runtime targets Linux amd64 images")
    return {
        "id": data["Id"],
        "repo_digests": data.get("RepoDigests", []),
        "architecture": data["Architecture"],
    }


def workspaces(source, output):
    output = Path(output).resolve()
    source = Path(source).resolve() if source != "-" else None
    if output.exists():
        raise ValueError(
            "Use a fresh output workspace; earlier attempts are never overwritten"
        )
    if source is not None and (not source.is_dir() or output.is_relative_to(source)):
        raise ValueError(
            "Input must be a directory and output must be outside that input tree"
        )
    if any(
        c in str(output) or (source is not None and c in str(source))
        for c in [":", ",", "\n", "\r"]
    ):
        raise ValueError(
            "Container workspace paths may not contain colon, comma or newlines"
        )
    return source, output


def execute(runtime, image, source, output, command, online=False):
    source, output = workspaces(source, output)
    identity = (
        image_identity(image)
        if runtime == "docker"
        else {"sif_sha256": sha(image), "path": str(Path(image).resolve())}
    )
    output.mkdir(parents=True)
    record = {
        "schema_version": "1",
        "runtime": runtime,
        "image": identity,
        "command": command,
        "input_workspace": str(source) if source else None,
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "exit_code": None,
        "network": ("bridge" if online else "none")
        if runtime == "docker"
        else "host (Apptainer does not isolate networking by default)",
    }
    cid = None
    code = 2
    try:
        if runtime == "docker":
            args = [
                "docker",
                "create",
                "--network",
                "bridge" if online else "none",
                "--read-only",
                "--tmpfs",
                "/tmp:rw,nosuid,nodev",
                "--volume",
                "/work",
                "--workdir",
                "/work",
                "--user",
                f"{os.getuid()}:{os.getgid()}",
                "--env",
                "HOME=/tmp",
                identity["id"],
                *command,
            ]
            cid = call(args, capture_output=True, text=True).stdout.strip()
            if source:
                call(["docker", "cp", "--archive", str(source) + "/.", cid + ":/work"])
            # docker start does not reliably propagate the application exit code.
            started = subprocess.run(["docker", "start", "--attach", cid])
            state = json.loads(
                call(["docker", "inspect", cid], capture_output=True, text=True).stdout
            )[0]["State"]
            code = (
                state["ExitCode"]
                if state["Status"] == "exited"
                else (started.returncode or 2)
            )
            record["container_state"] = state
            call(["docker", "cp", "--archive", cid + ":/work/.", str(output)])
        else:
            if source:
                shutil.copytree(source, output, dirs_exist_ok=True)
            args = [
                "apptainer",
                "exec",
                "--cleanenv",
                "--containall",
                "--no-home",
                "--no-mount",
                "cwd,hostfs",
                "--bind",
                str(output) + ":/work:rw",
                "--pwd",
                "/work",
                "--env",
                "HOME=/tmp",
                str(Path(image).resolve()),
                *command,
            ]
            code = subprocess.run(args).returncode
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        record["error"] = f"{type(exc).__name__}: {exc}"
        code = code or 2
    finally:
        if cid:
            # Remove only the temporary container/anonymous volume created above.
            cleanup = subprocess.run(
                ["docker", "rm", "--force", "--volumes", cid],
                capture_output=True,
                text=True,
            )
            if cleanup.returncode:
                record["cleanup_error"] = cleanup.stderr
        record["exit_code"] = code
        record["finished_utc"] = datetime.now(timezone.utc).isoformat()
        evidence = output / ".container-runs"
        evidence.mkdir(exist_ok=True)
        (evidence / (uuid.uuid4().hex + ".json")).write_text(
            json.dumps(record, indent=2) + "\n"
        )
    return code


def build_sif(image, output):
    output = Path(output).resolve()
    if output.exists():
        raise ValueError(
            "Use a fresh SIF filename; do not replace cached image content"
        )
    identity = image_identity(image)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix="traffic-sif-", dir=os.environ.get("APPTAINER_TMPDIR")
    ) as temp:
        temp = Path(temp)
        archive = temp / "image.tar"
        call(["docker", "image", "save", "--output", str(archive), identity["id"]])
        cache = temp / "cache"
        cache.mkdir()
        env = {
            **os.environ,
            "APPTAINER_CACHEDIR": str(cache),
            "APPTAINER_TMPDIR": str(temp),
        }
        help_text = call(
            ["apptainer", "build", "--help"], capture_output=True, text=True
        ).stdout
        build_args = ["--ignore-proot"] if "--ignore-proot" in help_text else []
        call(
            [
                "apptainer",
                "build",
                *build_args,
                str(output),
                "docker-archive:" + str(archive),
            ],
            env=env,
        )
    fingerprint = sha(output)
    receipt = {
        "schema_version": "1",
        "source_oci": identity,
        "sif_sha256": fingerprint,
        "apptainer": call(
            ["apptainer", "--version"], capture_output=True, text=True
        ).stdout.strip(),
    }
    output.with_suffix(output.suffix + ".json").write_text(
        json.dumps(receipt, indent=2) + "\n"
    )
    output.with_suffix(output.suffix + ".sha256").write_text(
        fingerprint + "  " + output.name + "\n"
    )
    print(json.dumps({"sif": str(output), **receipt}, indent=2))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    for action in ["run", "run-online"]:
        p = sub.add_parser(action)
        p.add_argument("runtime", choices=["docker", "apptainer"])
        p.add_argument("image")
        p.add_argument("input")
        p.add_argument("output")
        p.add_argument("args", nargs=argparse.REMAINDER)
    p = sub.add_parser("smoke")
    p.add_argument("runtime", choices=["docker", "apptainer"])
    p.add_argument("image")
    p.add_argument("output")
    p = sub.add_parser("sif-build")
    p.add_argument("image")
    p.add_argument("output")
    args = parser.parse_args(argv)
    try:
        if args.action == "sif-build":
            return build_sif(args.image, args.output)
        if args.action == "smoke":
            return execute(
                args.runtime, args.image, "-", args.output, ["/bin/sh", "-c", SMOKE]
            )
        command = args.args
        if command[:1] == ["--"]:
            command = command[1:]
        if not command:
            parser.error("Provide model CLI arguments, for example doctor")
        return execute(
            args.runtime,
            args.image,
            args.input,
            args.output,
            ["autonomous-traffic", *command],
            args.action == "run-online",
        )
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"container error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
