FROM python:3.7

WORKDIR /app

ADD . .
ARG DEPLOY_KEY
RUN mkdir -p /root/.ssh && \
    echo $DEPLOY_KEY | base64 -d > /root/.ssh/id_rsa && chmod 600 /root/.ssh/id_rsa && \
    pip install pipenv && \
    ssh-keyscan git.bink.com > /root/.ssh/known_hosts && \
    pipenv install --system
