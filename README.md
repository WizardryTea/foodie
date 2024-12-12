# Проект Foodie

## Описание

Foodie - это веб-приложение для общения между посетителями одной сети кафе.

## Установка

### Шаги по установке

1. Клонируйте репозиторий:
$ git clone https://github.com/WizardryTea/foodie.git

2. Создайте виртуальное окружение (для Windows и Мак соответственно)
$  python -m venv venv
$  python3 -m venv venv

3. Активируйте виртуальное окружение (для Windows и Мак соответственно)
$  source venv/scripts/activate
$  source venv/bin/activate

4. Перейдите в директорию проекта
cd foodie

5. Установите зависимости
$  pip install -r requirements.txt

6. Создайте миграции. После создания модели необходимо создать миграцию (для Windows и Мак соответственно)
$ python manage.py makemigrations
$ python manage.py migrate

7. Запустите сервер (для Windows и Мак соответственно)
$ python manage.py runserver
$ python3 manage.py runserver

8. Создайте суперадмина (для Windows и Мак соответственно)
$  python manage.py createsuperuser
$  python3 manage.py createsuperuser

Теперь наш сервер доступен по адресу http://127.0.0.1:8000/ в браузере.
