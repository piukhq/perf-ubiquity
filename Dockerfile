FROM python:3.7

WORKDIR /app

RUN pip install pipenv && pipenv install --system --deploy
