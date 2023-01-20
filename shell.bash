#!/bin/bash

python3 manage.py makemigrations
python3 manage.py migrate
service nginx start
gunicorn --bind unix:/tmp/gunicorn.sock config.wsgi:application
