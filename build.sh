#!/usr/bin/env bash
set -o errexit

mkdir -p /var/data
mkdir -p /var/data/media

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate