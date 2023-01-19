#!/bin/sh


python3 manage.py crontab add
python3 manage.py makemigrations
python3 manage.py migrate

