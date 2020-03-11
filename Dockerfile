FROM python:3.8
ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
#RUN python ./meta_social/manage.py makemigrations
RUN python ./meta_social/manage.py migrate
RUN python ./meta_social/manage.py loaddata ./meta_social/db.json

