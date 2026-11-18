"""Independent deterministic random streams for exogenous inputs."""

import hashlib
import random


def random_stream(seed, name):
    key = hashlib.sha256(f"traffic-demand-v1:{seed}:{name}".encode()).digest()
    return random.Random(int.from_bytes(key, "big"))
