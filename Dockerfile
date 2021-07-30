FROM ghcr.io/binkhq/python:3.9

WORKDIR /app

ADD . .
RUN pip install pipenv && \
    pipenv install --system && \
    apt update && apt -y install vim nano tmux postgresql-client && apt-get clean
