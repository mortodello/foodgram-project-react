# Проект Foodgram

[![Main Foodgram workflow](https://github.com/mortodello/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg?branch=master)](https://github.com/mortodello/foodgram-project-react/actions/workflows/foodgram_workflow.yml)

## Ссылка на проект
[Foodgram](https://bertysfoodgram.hopto.org)

## Администратор проекта

- email: sixhouse666@yandex.ru
- username: Dagot_Ur
- password: slo390WU

## Описание
Проект "Foodgram" – это "продуктовый помощник". На этом сервисе авторизированные пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд. Для неавторизированных пользователей доступны просмотр рецептов и страниц авторов.

## Как запустить проект на боевом сервере:
- Установить на сервере docker и docker-compose. Скопировать на сервер файлы docker-compose.yaml и default.conf:
```sh
scp docker-compose.yml
<логин_на_сервере>@<IP_сервера>:/home/<логин_на_сервере>/docker-compose.yml
```
```sh
scp nginx.conf <логин_на_сервере>@<IP_сервера>:/home/<логин_на_сервере>/nginx.conf
```

- Добавить в Secrets на Github следующие данные:
DB_ENGINE=django.db.backends.postgresql # указать, что проект работает с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД
DB_HOST=db # название сервиса БД (контейнера) 
DB_PORT=5432 # порт для подключения к БД
DOCKER_PASSWORD= # Пароль от аккаунта на DockerHub
DOCKER_USERNAME= # Username в аккаунте на DockerHub
HOST= # IP удалённого сервера
USER= # Логин на удалённом сервере
SSH_KEY= # SSH-key компьютера, с которого будет происходить подключение к удалённому серверу
PASSPHRASE= #Если для ssh используется фраза-пароль
TELEGRAM_TO= #ID пользователя в Telegram
TELEGRAM_TOKEN= #ID бота в Telegram

- Выполнить команды:
```sh
git add .
git commit -m "Коммит"
git push
```
- После этого будут запущены процессы workflow:
сборка и доставка докер-образа для контейнера web на Docker Hub
автоматический деплой проекта на боевой сервер
отправка уведомления в Telegram о том, что процесс деплоя успешно завершился

- После успешного завершения процессов workflow на боевом сервере должны будут выполнены следующие команды:
```sh
sudo docker-compose exec web python manage.py migrate
sudo docker-compose exec web python manage.py collectstatic --no-input 
```

- Затем необходимо будет создать суперюзера и загрузить в базу данных информацию об ингредиентах:
```sh
sudo docker-compose exec web python manage.py createsuperuser

sudo docker-compose exec web python manage.py load_data_csv --path <путь_к_файлу> --model_name <имя_модели> --app_name <название_приложения>
```

## Как запустить проект локально в контейнерах:

- Клонировать репозиторий и перейти в него в командной строке:
```sh
git@github.com:mortodello/foodgram-project-react.git cd foodgram-project-react
```
- Перейти в папку infra:
```sh
cd infra
```
- Запустить докер и в папке infra выполнить команду:
```sh
docker compose -f docker-compose.local.yml up
```
- После создания и запуска контейнеров, открыть новый терминал и перейти в контейнер с бекэндом:
```sh
docker exec -it infra-backend-1 bash
```
- Внутри контейнера выполнить следующие команды:
```sh
python manage.py migrate

python manage.py collectstatic

python manage.py createsuperuser
```
- Локально проект будет доступен по адресу http://127.0.0.1:8000/ ✨Magic ✨

## В API доступны следующие эндпоинты:
- /api/users/ Get-запрос – получение списка пользователей. POST-запрос – регистрация нового пользователя. Доступно без токена.

- /api/users/{id} GET-запрос – персональная страница пользователя с указанным id (доступно без токена).

- /api/users/me/ GET-запрос – страница текущего пользователя. PATCH-запрос – редактирование собственной страницы. Доступно авторизированным пользователям.

- /api/users/set_password POST-запрос – изменение собственного пароля. Доступно авторизированным пользователям.

- /api/auth/token/login/ POST-запрос – получение токена. Используется для авторизации по емейлу и паролю, чтобы далее использовать токен при запросах.

- /api/auth/token/logout/ POST-запрос – удаление токена.

- /api/tags/ GET-запрос — получение списка всех тегов. Доступно без токена.

- /api/tags/{id} GET-запрос — получение информации о теге о его id. Доступно без токена.

- /api/ingredients/ GET-запрос – получение списка всех ингредиентов. Подключён поиск по частичному вхождению в начале названия ингредиента. Доступно без токена.

- /api/ingredients/{id}/ GET-запрос — получение информации об ингредиенте по его id. Доступно без токена.

- /api/recipes/ GET-запрос – получение списка всех рецептов. Возможен поиск рецептов по тегам и по id автора (доступно без токена). POST-запрос – добавление нового рецепта (доступно для авторизированных пользователей).

- /api/recipes/?is_favorited=1 GET-запрос – получение списка всех рецептов, добавленных в избранное. Доступно для авторизированных пользователей.

- /api/recipes/is_in_shopping_cart=1 GET-запрос – получение списка всех рецептов, добавленных в список покупок. Доступно для авторизированных пользователей.

- /api/recipes/{id}/ GET-запрос – получение информации о рецепте по его id (доступно без токена). PATCH-запрос – изменение собственного рецепта (доступно для автора рецепта). DELETE-запрос – удаление собственного рецепта (доступно для автора рецепта).

- api/recipes/{id}/favorite/ POST-запрос – добавление нового рецепта в избранное. DELETE-запрос – удаление рецепта из избранного. Доступно для авторизированных пользователей.

- /api/recipes/{id}/shopping_cart/ POST-запрос – добавление нового рецепта в список покупок. DELETE-запрос – удаление рецепта из списка покупок. Доступно для авторизированных пользователей.

- /api/recipes/download_shopping_cart/ GET-запрос – получение текстового файла со списком покупок. Доступно для авторизированных пользователей.

- /api/users/{id}/subscribe/ GET-запрос – подписка на пользователя с указанным id. POST-запрос – отписка от пользователя с указанным id. Доступно для авторизированных пользователей

- /api/users/subscriptions/ GET-запрос – получение списка всех пользователей, на которых подписан текущий пользователь Доступно для авторизированных пользователей.

## Автор проекта
Корсаков Сергей [mortodello]
