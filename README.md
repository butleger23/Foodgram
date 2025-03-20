### Описание проекта:

В данном проекте был создан бекенд и настроена работа сервера для Foodgram.

### Как развернуть проект локально:

Склонировать проект:

```
git clone https://github.com/butleger23/Foodgram.git
cd Foodgram
```

В корневой директории требуется создать .env файл с данными переменными
```
POSTGRES_USER=user_example
POSTGRES_PASSWORD=password_example
POSTGRES_DB=example_db
DB_HOST=db
DB_PORT=5432
DEBUG=False
ALLOWED_HOSTS='127.0.0.1, localhost:8000'
USE_SQLITE=False
```
USE_SQLITE - булевая переменная, определяющая какая база данных используется (sqlite/postgres)

Находясь в корневой директории выполнить

`docker compose up -d`

Проект будет доступен по url `http://localhost:8000/recipes`

### Спецификация API:

Находясь в корневой директории выполнить

`docker compose -f infra/docker-compose.yml up`

Документация будет доступна по url `http://localhost/api/docs/`

### Как наполнить базу данных тестовыми данными:

1) Локально:

Находясь в корневой директории выполнить

`python backend/manage.py import_ingredients backend/static/data/ingredients.csv`

2) При деплое на сервер БД уже должна быть наполнена при помощи github actions.

### Использованные технологии:

В данном проекте используются данные технологии:

[Django](https://www.djangoproject.com/)

[Django rest framework](https://www.django-rest-framework.org/)

[drf-extra-fields](https://github.com/Hipo/drf-extra-fields)

[reportlab](https://pypi.org/project/reportlab/)

### Адрес сервера:

Проект развернут:

[На домене: borpa.bounceme.net](https://borpa.bounceme.net/)

[По IP: https://51.250.101.197/](https://51.250.101.197/recipes)

### Примеры запросов и ответов API:
1) Запрос списка рецептов
http://localhost/api/recipes/

```
{
  "count": 123,
  "next": "http://foodgram.example.org/api/recipes/?page=4",
  "previous": "http://foodgram.example.org/api/recipes/?page=2",
  "results": [
    {
      "id": 0,
      "tags": [
        {
          "id": 0,
          "name": "Завтрак",
          "slug": "breakfast"
        }
      ],
      "author": {
        "email": "user@example.com",
        "id": 0,
        "username": "string",
        "first_name": "Вася",
        "last_name": "Иванов",
        "is_subscribed": false,
        "avatar": "http://foodgram.example.org/media/users/image.png"
      },
      "ingredients": [
        {
          "id": 0,
          "name": "Картофель отварной",
          "measurement_unit": "г",
          "amount": 1
        }
      ],
      "is_favorited": true,
      "is_in_shopping_cart": true,
      "name": "string",
      "image": "http://foodgram.example.org/media/recipes/images/image.png",
      "text": "string",
      "cooking_time": 1
    }
  ]
}
```
2) Добавить рецепт в избранное http://localhost/api/recipes/{id}/favorite/

```
{
  "id": 0,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.png",
  "cooking_time": 1
}
```
3) Создание рецепта http://localhost/api/recipes/

Тело запроса:
```
{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```
Ответ:
```
{
  "id": 0,
  "tags": [
    {
      "id": 0,
      "name": "Завтрак",
      "slug": "breakfast"
    }
  ],
  "author": {
    "email": "user@example.com",
    "id": 0,
    "username": "string",
    "first_name": "Вася",
    "last_name": "Иванов",
    "is_subscribed": false,
    "avatar": "http://foodgram.example.org/media/users/image.png"
  },
  "ingredients": [
    {
      "id": 0,
      "name": "Картофель отварной",
      "measurement_unit": "г",
      "amount": 1
    }
  ],
  "is_favorited": true,
  "is_in_shopping_cart": true,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.png",
  "text": "string",
  "cooking_time": 1
}
```
### Авторы проекта:

Данный проект был разработан Максименко Стефаном
