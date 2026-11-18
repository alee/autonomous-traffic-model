"""Deterministic request serialization and content hashes."""

import hashlib
import json


def write_outputs(records, output, config_bytes):
    output.mkdir(parents=True, exist_ok=True)
    payloads = {}
    for name, value in records.items():
        if name == "summary":
            payloads[name + ".json"] = (
                json.dumps(value, indent=2, sort_keys=True) + "\n"
            )
        else:
            payloads[name + ".jsonl"] = "".join(
                json.dumps(row, sort_keys=True) + "\n" for row in value
            )
    manifest = {
        "input_sha256": hashlib.sha256(config_bytes).hexdigest(),
        "files": {
            name: hashlib.sha256(data.encode()).hexdigest()
            for name, data in sorted(payloads.items())
        },
    }
    payloads["files-manifest.json"] = (
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )
    for name, content in payloads.items():
        target = output / name
        if target.exists() and target.read_text() != content:
            raise ValueError(
                f"Output conflict: {target}; choose a new output directory"
            )
    for name, content in payloads.items():
        (output / name).write_text(content)
    return manifest
