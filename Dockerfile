FROM python:3.7

WORKDIR /app

ADD . .
ARG DEPLOY_KEY
RUN echo $DEPLOY_KEY | base64 -d > /root/.ssh/id_rsa && chmod 600 /root/.ssh/id_rsa && \
    pip install pipenv && \
    pipenv install --system

