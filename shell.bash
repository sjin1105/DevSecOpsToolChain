#!/bin/bash

python3 manage.py makemigrations
python3 manage.py migrate

gunicorn --bind unix:/tmp/gunicorn.sock config.wsgi:application
service nginx start
