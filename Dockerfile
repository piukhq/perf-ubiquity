FROM ghcr.io/binkhq/python:3.9-pipenv

WORKDIR /app
ADD . .

RUN apt update && apt -y install gcc vim nano tmux postgresql-client && \
    pipenv install --deploy --system --ignore-pipfile && \
    apt-get autoremove -y gcc && rm -rf /var/lib/apt/lists/*
