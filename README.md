# Агрегатор социальных сетей (МетаСоциальнаяСеть)

> Руководитель проекта : Кропотухин Алексей 
>
> Время проведения совещаний: Среда 20:00


## Что делать при первом запуске проекта?

1. Клонируем репозиторий, создаем и активируем venv, устанавливаем библиотеки

        git clone https://gitlab.informatics.ru/2019-2020/online/s101/meta-social.git
        cd meta-social
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt

2. Накатываем миграции

        cd meta_social
        python manage.py makemigrations
        python manage.py migrate


## Что делать если django не видит миграции?

Удаляем **db.sqlite3** и папку **migrations**, затем вводим

    python manage.py makemigrations meta_social_app
    python manage.py migrate
