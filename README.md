# Meta Social
[![Tests CI](https://github.com/PickBas/meta-social/actions/workflows/tests.yml/badge.svg)](https://github.com/PickBas/meta-social/actions/workflows/tests.yml)

> Team lead : Kropotuhin Alex 

## How do you run the project?

1. Clone the repo, create venv, install all the libraries

        git clone https://github.com/PickBas/meta-social.git
        cd meta-social
        python -m venv venv
        . ./venv/bin/activate
        pip install -U pip
        pip install -r requirements.txt

3. Get your migrations ready, import allath.json

        python manage.py makemigrations
        python manage.py migrate
        python manage.py loaddata allauth.json

4. Running the project

    #### Using Docker:

        docker-compose up --build
    
    #### Without Docker:

        python manage.py runserver
        celery -A meta_social worker -l info

## How do you create admin user?

Use custom manage.py command:

    python manage.py createsuperuser_ms
