FROM --platform=amd64 python:3.10-slim-buster

WORKDIR /bot

RUN pip install poetry

COPY pyproject.toml /bot
COPY poetry.lock /bot

RUN poetry install

COPY . /bot

CMD ["sh", "entrypoint.sh"]
