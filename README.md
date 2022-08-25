## Foodgram

Foodgram это «Продуктовый помощник» на этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.
Автор проекта студентка курса Яндекс.Практикум Пересада Светлана.

## **Технологии**

Python 3.7, Django 3.0.5, Django REST Framework 3.11, PostgresQL, Docker, Yandex.Cloud.

## **Запуск проекта**

Необхoдимо скачать проект выполнив команду:

```
git clone git@github.com:PeresadaSvetlana/foodgram-project-react.git
```

Перейти в папку cd infra cоздать файл .env с параметрами:

```
DB_ENGINE=<django.db.backends.postgresql>
DB_NAME=<имя базы данных postgres>
DB_USER=<пользователь бд>
DB_PASSWORD=<пароль>
DB_HOST=<db>
DB_PORT=<5432>
SECRET_KEY=<секретный ключ проекта django>
```
Выполнить команду:

```
docker-compose up -d --build
```





