FROM python:3.7

WORKDIR /app

ADD . .
RUN pip install "pipenv==2018.11.26" && \
    pipenv install --system && \
    apt update && apt -y install vim nano tmux postgresql-client && apt-get clean
