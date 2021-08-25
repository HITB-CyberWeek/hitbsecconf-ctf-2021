#!/bin/bash

set +ex

python /app/migrate.py

gunicorn -k uvicorn.workers.UvicornWorker -c /app/gunicorn_conf.py app:app