# DevOps Task Tracker

Функциональное веб-приложение для отслеживания задач внутри команды. 
Реализована система разграничения прав, JWT-аутентификация, панель администратора и интерфейс на Vue 3.

# Технологический стек
## Backend
- Python 3.11
- Django 5.2
- Django REST Framework
- Simple JWT
- PostgreSQL
- pytest (тестирование)

## Frontend
- Vue.js 3 (Composition API)
- Pinia (store)
- Axios
- Vue Router
- Vite

## Инфраструктура
- Docker
- Docker Compose
- Nginx (проксирование)

## Возможности
- Авторизация по JWT
- Разделение ролей: администратор и сотрудник
- Управление задачами (CRUD)
- Управление пользователями через Django admin
- Панель администратора с кастомными моделями
- Интерфейс с защитой маршрутов
- Подробная документация кода
- Тестовое покрытие кода

# Установка и запуск
1. Клонировать репозиторий 
```bash
git clone https://github.com/bakharevd/devops-task-tracker.git
cd devops-task-tracker
```

2. Создать `.env` файл 
```bash
cp .env.example .env
```

3. Заполнить `.env` файл необходимыми переменными окружения:
```env
# Django
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL
POSTGRES_DB=devops_db
POSTGRES_USER=devops_user
POSTGRES_PASSWORD=devops_pass
POSTGRES_HOST=db
POSTGRES_PORT=5432

# JWT
JWT_ACCESS_LIFETIME_MINUTES=30
JWT_REFRESH_LIFETIME_DAYS=1
```

4. Собрать и запустить контейнеры 
```bash
docker-compose up --build
```

Приложение будет доступно по адресам:
- Backend API: http://localhost:8000/api
- Admin-панель: http://localhost:8000/admin
- Frontend: http://localhost

# Создание первого пользователя
После запуска контейнеров создайте суперпользователя:
```bash
docker-compose exec backend python manage.py createsuperuser
```

# Тесты и покрытие
Запуск тестов:
```bash
docker-compose exec backend pytest
```

Генерация отчета о покрытии:
```bash
docker-compose exec backend pytest --cov
```

# Документация
Проект содержит подробную документацию:
- Документация моделей и их полей
- Документация API эндпоинтов
- Документация представлений и сериализаторов
- Документация разрешений и прав доступа
- Документация административного интерфейса

# Структура проекта
```
tree -a -I '.git|*.pyc|.env|node_modules|staticfiles|migrations|.venv|__pycache__|.idea|.vscode|.pytest_cache|.coverage'
.
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
│   │   │   ├── management
│   │   │   │   ├── __init__.py
│   │   │   │   └── commands
│   │   │   │       ├── __init__.py
│   │   │   │       └── populate_test_data.py
│   │   │   ├── models.py
│   │   │   ├── permissions.py
│   │   │   ├── serializers.py
│   │   │   ├── serializers_comment.py
│   │   │   ├── tests.py
│   │   │   ├── urls.py
│   │   │   └── views.py
│   │   └── users
│   │       ├── __init__.py
│   │       ├── admin.py
│   │       ├── apps.py
│   │       ├── models.py
│   │       ├── permissions.py
│   │       ├── serializers.py
│   │       ├── tests.py
│   │       ├── urls.py
│   │       └── views.py
│   ├── config
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── entrypoint.sh
│   ├── manage.py
│   ├── pytest.ini
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
    │   └── logo.png
    ├── src
    │   ├── App.vue
    │   ├── components
    │   │   ├── LoginForm.vue
    │   │   ├── ProjectForm.vue
    │   │   ├── ProjectList.vue
    │   │   ├── TaskDetail.vue
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
    │       ├── index.js
    │       └── uiStyles.js
    └── vite.config.js

19 directories, 56 files
```

# Авторизация и роли
- Для API используется JWT через пакет SimpleJWT
- Авторизация на фронтенде: access/refresh токены хранятся в localStorage
- Роли пользователей ("user", "admin") определяются на уровне модели
- Время жизни токенов настраивается через переменные окружения

# Админка
- Поддержка редактирования моделей: `Task`, `User`
- Кнопка "Просмотреть сайт" ведёт на /tasks
- Кастомизированный интерфейс для удобного управления данными

> Проект разработан с учётом расширяемости и дальнейшего масштабирования. 
> Подходит как для демонстрации, так и для боевого использования внутри команды DevOps.


