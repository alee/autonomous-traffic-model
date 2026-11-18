ARG BASE_IMAGE=python@sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df
FROM ${BASE_IMAGE}

# Runtime shared libraries required by the pinned SUMO wheel, including its headless binary.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libx11-6 libxext6 libstdc++6 libgomp1 libxrender1 libatomic1 \
    && rm -rf /var/lib/apt/lists/*
COPY deploy/htcondor/requirements.lock /opt/requirements.lock
COPY dist/htc/autonomous_traffic_model-0.1.0-py3-none-any.whl /opt/wheels/
RUN python -m pip install --no-cache-dir --require-hashes -r /opt/requirements.lock \
    && python -m pip install --no-cache-dir --no-deps /opt/wheels/*.whl \
    && rm -rf /opt/wheels \
    && useradd --uid 10001 --create-home traffic \
    && mkdir -p /work \
    && chown traffic:traffic /work
ENV PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
USER traffic
WORKDIR /work
CMD ["autonomous-traffic", "doctor"]
