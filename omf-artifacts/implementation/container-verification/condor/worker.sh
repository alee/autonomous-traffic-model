#!/bin/sh
set -eu
export PYTHONDONTWRITEBYTECODE=1
exec autonomous-traffic htc-run "$@"
