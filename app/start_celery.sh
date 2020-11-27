#!/bin/bash
cd /usr/src/app
celery -A tasks worker --loglevel=INFO
