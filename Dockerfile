FROM python:3.7

WORKDIR /app

ADD . .
ARG DEPLOY_KEY
RUN mkdir -p /root/.ssh && \
    echo $DEPLOY_KEY | base64 -d > /root/.ssh/id_rsa && chmod 600 /root/.ssh/id_rsa && \
    pip install "pipenv==2018.11.26" && \
    ssh-keyscan git.bink.com > /root/.ssh/known_hosts && \
    pipenv install --system && \
    apt update && apt -y install vim tmux postgresql-client && apt-get clean
