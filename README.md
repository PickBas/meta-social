# Meta Social

> Team lead : Kropotuhin Alex 

## How do you run the project?

1. Clone the repo, create venv, install all the libraries

        git clone https://gitlab.informatics.ru/2019-2020/online/s101/meta-social.git
        cd meta-social
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt

2. Get your migrations ready, import allath.json

        cd meta_social
        python manage.py makemigrations
        python manage.py migrate
        python manage.py loaddata allauth.json

3. Running the project

    #### Using Docker:

        docker-compose up --build
    
    #### Without Docker:

        python manage.py runserver
        celery -A meta_social worker -l info

## How do you create admin user?

Use custom manage.py command:

    python manage.py createsuperuser_ms
