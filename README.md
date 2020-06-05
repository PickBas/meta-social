# Агрегатор социальных сетей (МетаСоциальнаяСеть)

> Руководитель проекта : Кропотухин Алексей 
>
> Время проведения совещаний: Среда 20:00


## Как запустить проект?

1. Клонируем репозиторий, создаем и активируем venv, устанавливаем библиотеки

        git clone https://gitlab.informatics.ru/2019-2020/online/s101/meta-social.git
        cd meta-social
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt

2. Накатываем миграции, и импортируем бд

        cd meta_social
        python manage.py makemigrations
        python manage.py migrate
        python manage.py loaddata allauth.json

3. Запуск проекта

    #### Используя docker:

        docker-compose up --build
    
    #### Без docker:

        python manage.py runserver
        celery -A meta_social worker -l info

## Как создать админа?

Из-за кастомного профиля админ создается криво, так что делаем так и не паримся

    python manage.py createsuperuser_ms


# Данные о соц. сетях

## VK

Приложение

    id: 7317110
    key: ST3oRjWFifOgxxFUl5sH

## Facebook

Приложение

    id: 2555976281192292
    key: b82697d96b942c6f0aa253668c15eb6d

Тестовый пользователь

    # 1
    login: test_pzymgqq_user@tfbnw.net
    password: verystrongpa55word
    
    # 2
    login: vzsdnhqifk_1582663185@tfbnw.net
    password: verystrongpa55word

## Yandex

Приложение

    id: 1ff42eb87f8e4467807e3d8a9932424e
    key: 8d552db3599c4126ad977c3ed51498b5

# Для работы чата

## Запуск приложения через Docker
    docker-compose up --build

## Запуск на локальной машине
    CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('redis', 6379)], Заменить на "hosts": [('127.0.0.1', 6379)],
            },
        },
    }

## Установка redis
    Arch: sudo pacman -S redis
    Fedora: sudo dnf install redis
    Debian: sudo apt install redis

## Запуск redis
    Linux: redis-server
    Docker: docker run -p 6379:6379 -d redis:5

## Проверка redis
    redis-cli ping
