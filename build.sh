#!/usr/bin/env bash
# upgrade pip
python -m pip install --upgrade pip

# install requirements
pip install -r requirements.txt

# install django explicitly
pip install django

# run django commands
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput