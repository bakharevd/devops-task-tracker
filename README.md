# DevOps Task Tracker

Функциональное веб-приложение для отслеживания задач внутри команды. 
Реализована система разграничения прав, JWT-аутентификация, панель администратора и интерфейс на Vue 3.

# Технологический стек
## Backend
- Python 3.12
- Django 5.0
- Django REST Framework
- Simple JWT
- PostgreSQL

## Frontend
- Vue.js 3 (Composition API)
- Pinia (store)
- Axios
- Vue Router
- Vite

## Инфраструктура
- Docker
- Docker Compose

## Возможности
- Авторизация по JWT
- Разделение ролей: администратор и сотрудник
- Управление задачами (CRUD)
- Управление пользователями через Django admin
- Панель администратора с кастомными моделями
- Интерфейс с защитой маршрутов

# Установка и запуск
1. Клонировать репозиторий 
```
git clone https://github.com/bakharevd/devops-task-tracker.git
cd devops-task-tracker
```

2. Создать `.env` файл 
```
cp .env.example .env
```

3. Заполнить `.env`

4. Собрать и запустить контейнеры 
```
docker-compose up --build
```

Приложение будет доступно по адресам:
- Backend: http://localhost:8000/api
- Admin-панель: http://localhost/admin
- Frontend: http://localhost

# Создать первого пользователя (после запуска контейнеров)
```
docker-compose exec backend python manage.py createsuperuser
```

# Структура проекта
```
tree -a -I '.git|*.pyc|.env|node_modules|staticfiles|migrations|.venv|__pycache__|.idea' 
├── .env.example
├── .gitignore
├── README.md
├── backend
│   ├── Dockerfile
│   ├── apps
│   │   ├── tasks
│   │   │   ├── __init__.py
│   │   │   ├── admin.py
│   │   │   ├── apps.py
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── urls.py
│   │   │   └── views.py
│   │   └── users
│   │       ├── __init__.py
│   │       ├── admin.py
│   │       ├── apps.py
│   │       ├── models.py
│   │       ├── permissions.py
│   │       ├── serializers.py
│   │       ├── urls.py
│   │       └── views.py
│   ├── config
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── entrypoint.sh
│   ├── manage.py
│   └── requirements.txt
├── deploy
│   └── nginx
│       └── conf.d
│           └── default.conf
├── docker-compose.yml
└── frontend
    ├── .gitignore
    ├── Dockerfile
    ├── index.html
    ├── package-lock.json
    ├── package.json
    ├── public
    ├── src
    │   ├── App.vue
    │   ├── components
    │   │   ├── LoginForm.vue
    │   │   ├── TaskForm.vue
    │   │   ├── TaskList.vue
    │   │   └── layouts
    │   │       └── HeaderLayout.vue
    │   ├── main.js
    │   ├── router
    │   │   └── index.js
    │   ├── services
    │   │   └── api.js
    │   └── store
    │       └── index.js
    └── vite.config.js

17 directories, 43 files
```

# Авторизация и роли
- Для API используется JWT через пакет SimpleJWT
- Авторизация на фронтенде: access/refresh токены хранятся в localStorage
- Роли пользователей ("user", "admin") определяются на уровне модели

# Админка
- Поддержка редактирования моделей: `Task`, `User`
- Кнопка "Просмотреть сайт" ведёт на /tasks

> Проект разработан с учётом расширяемости и дальнейшего масштабирования. Подходит как для демонстрации, так и для боевого использования внутри команды DevOps.