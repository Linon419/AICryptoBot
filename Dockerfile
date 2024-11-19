FROM python:3.12-slim as pybuilder
WORKDIR /app
RUN pip3 install pdm==2.20.1
# copy pyproject.toml and pdm.lock
COPY pyproject.toml pdm.lock ./
RUN pdm config python.use_venv false && pdm install

