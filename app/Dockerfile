FROM python:3.8.6-slim
WORKDIR /usr/src/app
RUN apt-get update
RUN apt-get -y install docker.io
COPY requirements.txt /usr/src/app
RUN pip install -r /usr/src/app/requirements.txt
COPY .env /usr/src/app
COPY settings.py /usr/src/app
COPY tasks.py /usr/src/app
COPY app.py /usr/src/app
COPY start_celery.sh /usr/src/app
