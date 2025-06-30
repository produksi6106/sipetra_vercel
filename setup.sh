#!/bin/bash

# install dependancies
pip install setuptools
pip install -r requirements.txt

# Run django commands
python3.9 manage.py makemigrations
python3.9 manage.py migrate
python3.9 manage.py tailwind install
python3.9 manage.py collectstatic
#python3.9 manage.py tailwind start  # (jangan aktifkan ini di production)
