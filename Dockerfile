FROM ghcr.io/binkhq/python:3.11-poetry as build
WORKDIR /src
ADD . .
RUN poetry build

WORKDIR /tmp/copy
RUN cp /src/dist/*.whl .
WORKDIR /tmp/copy/locust_angelia
RUN cp -R /src/ubiquity_performance_test/locust_angelia/locustfile* .
WORKDIR /tmp/copy/locust_ubiquity
RUN cp -R /src/ubiquity_performance_test/locust_ubiquity/locustfile* .

FROM ghcr.io/binkhq/python:3.11 as main

ARG PIP_INDEX_URL=https://269fdc63-af3d-4eca-8101-8bddc22d6f14:b694b5b1-f97e-49e4-959e-f3c202e3ab91@pypi.gb.bink.com/simple
ARG wheel=ubiquity_performance_test-*-py3-none-any.whl

WORKDIR /app
COPY --from=build /tmp/copy/ ./

RUN apt update && \
    apt -y install gcc vim nano tmux postgresql-client

RUN pip install $wheel && \
    rm $wheel 

RUN apt -y autoremove gcc && \
    rm -rf /var/lib/apt/lists/*
