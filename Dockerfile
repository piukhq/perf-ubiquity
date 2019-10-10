FROM python:3.7

WORKDIR /app

ADD . .

RUN pip install pipenv && \
    pipenv install --system

