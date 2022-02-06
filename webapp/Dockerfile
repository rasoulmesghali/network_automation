# pull the official docker image
FROM tiangolo/uvicorn-gunicorn:python3.8

# set work directory
WORKDIR /app/

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./src/requirements.txt /app/

RUN pip3 install -r requirements.txt

COPY ./src/app /app/