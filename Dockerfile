FROM python:3.11.3-slim-bullseye

RUN python3 -m pip install pip-tools

WORKDIR /epistemix-community-library

COPY requirements.txt tmp/requirements.txt
COPY requirements_dev.txt tmp/requirements_dev.txt
RUN python3 -m pip install -r tmp/requirements.txt
RUN python3 -m pip install -r tmp/requirements_dev.txt
