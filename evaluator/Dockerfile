FROM python:3.8.6-slim
WORKDIR /usr/src/app
COPY requirements.txt /usr/src/app
RUN pip install -r /usr/src/app/requirements.txt
COPY app.py /usr/src/app
CMD python /usr/src/app/app.py
