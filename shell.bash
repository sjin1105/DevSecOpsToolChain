#!/bin/bash

python3 manage.py makemigrations
python3 manage.py migrate

DJANGO_SUPERUSER_USERNAME=admin
export DJANGO_SUPERUSER_USERNAME
DJANGO_SUPERUSER_EMAIL=admin@email.com
export DJANGO_SUPERUSER_EMAIL
DJANGO_SUPERUSER_PASSWORD=dkagh1.
export DJANGO_SUPERUSER_PASSWORD
python3 manage.py createsuperuser --noinput

service nginx start
gunicorn --bind unix:/tmp/gunicorn.sock config.wsgi:application
