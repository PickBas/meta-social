FROM python:3.8
ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
#RUN python ./core/manage.py makemigrations
#RUN python ./core/manage.py migrate
#RUN python ./core/manage.py loaddata ./core/db.json

