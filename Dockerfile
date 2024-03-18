FROM python:3.10

RUN pip install --upgrade pip
RUN pip install poetry
RUN poetry config virtualenvs.create false

WORKDIR /app
COPY pyproject.toml .
RUN poetry install --no-root

COPY . .