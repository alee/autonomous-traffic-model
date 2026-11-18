# One OCI application image; convert this same image to SIF for Apptainer.
ARG BASE_IMAGE=python@sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df
FROM ${BASE_IMAGE} AS build
WORKDIR /build
COPY deploy/htcondor/build-requirements.lock /tmp/build-requirements.lock
RUN python -m pip install --no-cache-dir --require-hashes -r /tmp/build-requirements.lock
COPY pyproject.toml README.md ./
COPY src ./src
RUN python -m hatchling build -t wheel

FROM ${BASE_IMAGE} AS runtime
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libx11-6 libxext6 libstdc++6 libgomp1 libxrender1 libatomic1 \
    && rm -rf /var/lib/apt/lists/*
COPY deploy/htcondor/requirements.lock /opt/traffic/requirements.lock
RUN python -m pip install --no-cache-dir --require-hashes -r /opt/traffic/requirements.lock
COPY --from=build /build/dist/*.whl /tmp/wheels/
RUN python -m pip install --no-cache-dir --no-deps /tmp/wheels/*.whl \
    && rm -rf /tmp/wheels \
    && useradd --uid 10001 --create-home traffic \
    && mkdir -p /work \
    && chmod 1777 /work
COPY --chmod=0444 omf-artifacts/implementation/scenarios/coronado-benchmark.json /opt/traffic/examples/coronado-benchmark.json
COPY --chmod=0444 omf-artifacts/implementation/gis/*.json /opt/traffic/examples/gis/
RUN chmod -R a+rX /opt/traffic/examples
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PROJ_NETWORK=OFF HOME=/tmp
USER traffic
WORKDIR /work
# HTCondor supplies the executable; local wrappers explicitly invoke the CLI.
ENTRYPOINT []
CMD []
