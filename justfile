# Requires just >= 1.39. Model arguments stay in the Python CLI and scenario files.
set positional-arguments
export TRAFFIC_IMAGE := env('TRAFFIC_IMAGE', 'autonomous-traffic-model:dev')
export TRAFFIC_SIF := env('TRAFFIC_SIF', 'dist/containers/model.sif')

default:
    @just --list

# Install the locked native development/preparation environment.
setup:
    uv sync --locked --extra sumo --extra geo

# Run model, GIS and headless regression checks.
check:
    uv run --locked --extra sumo --extra geo python -m unittest discover -s tests -v
    uv run --locked --extra sumo --extra geo ruff check src scripts tests
    uv run --locked --extra sumo --extra geo ruff format --check src scripts tests

# Forward arguments safely to the authoritative native CLI.
model +args:
    uv run --locked --extra sumo --extra geo autonomous-traffic "$@"

# Shift the accepted benchmark clock without modifying its source.
scenario start output:
    uv run --locked --extra sumo --extra geo autonomous-traffic scenario-configure --base omf-artifacts/implementation/scenarios/coronado-benchmark.json --start-local "$1" --output "$2"

# Build the complete application from source; host uv/Python packages are unnecessary.
image-build:
    docker build --platform linux/amd64 --file deploy/htcondor/Dockerfile --tag "$TRAFFIC_IMAGE" .

# Run the CLI in Docker: INPUT directory (or - for empty), fresh OUTPUT, then CLI args.
docker input output +args:
    python3 scripts/containers.py run docker "$TRAFFIC_IMAGE" "$@"

# Explicit network access for GIS acquisition during preparation.
docker-online input output +args:
    python3 scripts/containers.py run-online docker "$TRAFFIC_IMAGE" "$@"

# Exercise a complete eight-task engineering batch inside offline Docker.
docker-demo output:
    python3 scripts/containers.py smoke docker "$TRAFFIC_IMAGE" "$1"

# Export the built Docker image and convert it into a fresh checksummed SIF.
sif-build output='dist/containers/model.sif':
    python3 scripts/containers.py sif-build "$TRAFFIC_IMAGE" "$1"

# Run the same CLI using an existing SIF; INPUT may be - for an empty workspace.
apptainer input output +args:
    python3 scripts/containers.py run apptainer "$TRAFFIC_SIF" "$@"

# Exercise the same eight-task engineering batch in Apptainer.
apptainer-demo output:
    python3 scripts/containers.py smoke apptainer "$TRAFFIC_SIF" "$1"

# Freeze an HTCondor batch and stage a SIF by its content hash. Does not submit.
condor-plan sweep output:
    uv run --locked --extra sumo --extra geo autonomous-traffic htc-plan --sweep "$1" --output "$2" --sif "$TRAFFIC_SIF"

# Use an immutable OCI reference or content-named OSDF SIF for larger deployments.
condor-plan-image sweep output image:
    uv run --locked --extra sumo --extra geo autonomous-traffic htc-plan --sweep "$1" --output "$2" --image "$3"

# Validate all batch/image digests and run only the available HTCondor dry-run parser.
preflight batch:
    uv run --locked --extra sumo --extra geo autonomous-traffic htc-preflight --batch "$1"
