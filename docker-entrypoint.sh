#!/bin/bash

cd meta_social || exit
echo "======Собираем статику======"
echo "Загрузка в s3 облако, это займет много времени"
python manage.py collectstatic --noinput


echo "======Таки ждем, пока постгра поднимется======"
while ! curl http://db:5432/ 2>&1 | grep '52'
do
  echo "Таки ждем....."
  sleep 1
done
echo "Таки дождались..........."

echo "======Накатываем миграции======"
python manage.py migrate
echo "======Разворачиваем фикстуры======"
python manage.py loaddata allauth.json

echo "======Стартуем сервер======"
python manage.py runserver 0.0.0.0:80