#!/bin/bash
cd /usr/src/app
celery -A app.celery worker --loglevel=INFO
