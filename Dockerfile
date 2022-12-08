# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

RUN mkdir /app 

COPY /fast-api-strawberry-docker /fast-api-strawberry-docker

COPY pyproject.toml /app 
WORKDIR /app
ENV PYTHONPATH=${PYTHONPATH}:${PWD} 
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev
WORKDIR ../

EXPOSE 8000
CMD [ "python3", "-m" , "uvicorn", "fast-api-strawberry-docker.main:app", "--host", "0.0.0.0", "--port", "8000"]

