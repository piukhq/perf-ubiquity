FROM python:3.7

WORKDIR /app

ADD . .

RUN pip install pipenv && \
    pipenv install --system && \
    chmod 700 locust-start.sh

ENTRYPOINT ["locust-start.sh"]

