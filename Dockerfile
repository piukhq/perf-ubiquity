FROM python:3.7

WORKDIR /app
ADD . .

RUN pip install pipenv && pipenv install --system --deploy \
    && chmod +x locust-start.sh

ENTRYPOINT ["/app/locust-start.sh"]
