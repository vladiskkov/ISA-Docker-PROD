#FROM python:3.11-alpine
#FROM python:3.10.11-slim-bullseye
FROM python:3.10-slim

ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN mkdir /srv/www
COPY ./ISA /srv/www/ISA
WORKDIR /srv/www/ISA

RUN apt-get update && apt-get upgrade -y
RUN apt-get install postgresql-server-dev-all gcc python3-dev musl-dev gunicorn -y

RUN pip install -r requirements.txt
