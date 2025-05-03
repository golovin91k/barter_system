# BARTER SYSTEM
![example workflow](https://github.com/golovin91k/barter_system/workflows/Main%20barter_system%20workflow/badge.svg)

Проект запущен по адресу: https://golovin-projects.ddns.net/barter_system/

## Описание проекта
**BARTER SYSTEM** - это платформа для обмена вещами. Пользователи могут создавать объявления о вещах, которые они готовы обменять. Пользователи могут направлять друг другу предложения для обмена вещами.


## Технологии проекта
В проекте используются следующие технологии:


| Backend:     | Frontend:    | Deploy:        |
| :------------| :------------| :--------------|
| Django 4.2   | HTML         | GitHub Actions |
| PostgreSQL   | CSS          | Docker         |
|              |              | Nginx          |


Для получения более подробной информации об использованных библиотеках смотри файл src/barter_system/requirements.txt
## Порядок запуска проекта на удаленном сервере:
На сервере должны быть установлены:
- nginx,
- docker,
- docker compose,
- pip

Создайте на сервере папку для проекта.
В неё скопируйте файл docker-compose.yml из папки infra.
В этой же папке на удаленном сервере создайте файл окружения .env с Вашими настройками по образцу:

> POSTGRES_DB=barter_system_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_HOST=barter_system_db
POSTGRES_PORT=5432

SECRET_KEY=key
ALLOWED_HOSTS=golovin-projects.ddns.net
DEBUG=False

Загрузите репозиторий на Ваш компьютер.
Скорректируйте настройки django (файл settings.py в папке src/barter_system/barter_system/settings.py):
- Измените переменные, исходя из настроек Вашего сервера:
> FORCE_SCRIPT_NAME = '/barter_system'
STATIC_URL = '/barter_system/statics/'
MEDIA_URL = '/barter_system/media/'

- Удалите переменную
> FORCE_SCRIPT_NAME = '/barter_system'

Настройте github actions, исходя из настроек main.yml
Настройте Nginx на Вашем удаленном сервере.
Делайте коммит и пуш репозитория.
Github actions дальше все сделает за Вас.

## Порядок запуска проекта на локальном сервере:
Загрузите репозиторий на Ваш компьютер.
Перейдите в папку src/.
Создайте и запустите виртуальное окружение.
Установите зависимости из requirements.txt

В папке с настройками проекта создайте файл окружения .env с аналогичными настройками, как для удаленного сервера.

Скорректируйте настройки django (файл settings.py в папке src/barter_system/barter_system/settings.py):
- Удалите переменную
> FORCE_SCRIPT_NAME = '/barter_system'

Из папки с файлом manage.py:
- выполните миграции: python manage.py migrate
- запустите отладочный сервер: python manage.py runserver

Проект покрыт тестами pytest-django

Автор проекта - Головин Кирилл
e-mail: golovin91k@gmail.com
tg: https://t.me/golovin91k