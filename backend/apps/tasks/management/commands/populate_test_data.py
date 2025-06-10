import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.users.models import Position
from ...models import Status, Priority, Project, Task, Comment

User = get_user_model()


class Command(BaseCommand):
    help = (
        "Заполняет БД реалистичными тестовыми данными:\n"
        "• 15+ должностей (Position)\n"
        "• 20+ пользователей (User) с паролем 'Kief22Mo'\n"
        "• 5 статусов (Status)\n"
        "• 5 приоритетов (Priority)\n"
        "• 15 проектов (Project) с 3–5 участниками\n"
        "• 7–15 задач (Task) на каждый проект, с разными статусами и приоритетами\n"
        "• 5–15 комментариев (Comment) на каждую задачу, с разными авторами\n"
        "• Создаётся суперпользователь (admin) с email s@bhrv.dev и паролем bhrv\n\n"
        "Запуск:\n  python manage.py populate_test_data\n"
        "В Docker:\n  docker-compose exec backend python manage.py populate_test_data"
    )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.NOTICE("Старт заполнения реалистичными данными...")
        )

        Position.objects.all().delete()
        pos_names = [
            "DevOps Engineer",
            "System Administrator",
            "Network Engineer",
            "Support Specialist",
            "Cloud Architect",
            "Backend Developer",
            "Frontend Developer",
            "QA Engineer",
            "Product Manager",
            "Business Analyst",
            "UX/UI Designer",
            "Security Specialist",
            "Database Administrator",
            "Release Manager",
            "SRE Engineer",
        ]
        positions = []
        for name in pos_names:
            pos = Position.objects.create(name=name)
            positions.append(pos)
            self.stdout.write(f"✓ Position: {name}")

        User.objects.all().delete()
        user_data = [
            ("Alexey", "Ivanov"),
            ("Maria", "Petrova"),
            ("Dmitry", "Sokolov"),
            ("Ekaterina", "Kuznetsova"),
            ("Igor", "Vasilev"),
            ("Olga", "Smirnova"),
            ("Sergey", "Popov"),
            ("Anna", "Nikolaeva"),
            ("Vladimir", "Morozov"),
            ("Julia", "Lebedeva"),
            ("Pavel", "Kiselev"),
            ("Elena", "Orlova"),
            ("Roman", "Fedorov"),
            ("Natalia", "Guseva"),
            ("Timur", "Sharipov"),
            ("Svetlana", "Kozlova"),
            ("Anton", "Voronov"),
            ("Irina", "Belova"),
            ("Mikhail", "Karpov"),
            ("Daria", "Semenova"),
        ]
        from django.contrib.auth.hashers import make_password

        hashed_pw = make_password("Kief22Mo")

        users = []
        for idx, (first, last) in enumerate(user_data, start=1):
            username = f"{first.lower()[0]}.{last.lower()}"
            email = f"{username}@bhrv.dev"
            position = random.choice(positions)
            user = User(
                username=username,
                email=email,
                password=hashed_pw,
                first_name=first,
                last_name=last,
                position=position,
                role="user",
                is_active=True,
            )
            user.save()
            users.append(user)
            self.stdout.write(
                f"✓ User #{idx}: {first} {last}, position={position.name}"
            )

        admin_email = "s@bhrv.dev"
        admin_user = User.objects.create(
            username="bhrv",
            email=admin_email,
            password=make_password("bhrv"),
            first_name="Semen",
            last_name="Bakharev",
            position=positions[0],
            role="admin",
            is_active=True,
            is_superuser=True,
            is_staff=True,
        )
        users.append(admin_user)
        self.stdout.write(f"✓ Admin user: {admin_email} (пароль: bhrv)")

        Status.objects.all().delete()
        status_names = ["Открыта", "В работе", "На проверке", "Завершена", "Отложена"]
        statuses = []
        for name in status_names:
            st = Status.objects.create(name=name)
            statuses.append(st)
            self.stdout.write(f"✓ Status: {name}")

        Priority.objects.all().delete()
        priority_levels = ["Низкий", "Средний", "Высокий", "Критический", "Блокирующий"]
        priorities = []
        for level in priority_levels:
            pr = Priority.objects.create(level=level)
            priorities.append(pr)
            self.stdout.write(f"✓ Priority: {level}")

        Project.objects.all().delete()
        project_templates = [
            (
                "Миграция на AWS",
                "Перенос инфраструктуры в облако AWS: контейнеризация, Terraform, настройка CI/CD.",
                "AWS",
            ),
            (
                "Внедрение мониторинга",
                "Установка и настройка Prometheus/Grafana для отслеживания производительности серверов.",
                "MON",
            ),
            (
                "Обновление сетевой инфраструктуры",
                "Замена устаревшего оборудования, настройка VLAN и QoS.",
                "NET",
            ),
            (
                "Резервное копирование и DR",
                "Организация регулярного бэкапа баз данных, настройка DR-плана.",
                "DR",
            ),
            (
                "Переход на Kubernetes",
                "Перенос микросервисов в k8s-кластер, настройка Helm-чартов.",
                "K8S",
            ),
            (
                "SSL и безопасность",
                "Установка Let's Encrypt, настройка WAF и сканирование уязвимостей.",
                "SSL",
            ),
            (
                "Внедрение CI/CD",
                "Настройка GitLab CI для проекта, автоматизация деплоя и тестирования.",
                "CICD",
            ),
            (
                "Оптимизация БД",
                "Ревизия индексов, настройка репликации, оптимизация SQL-запросов.",
                "DB",
            ),
            (
                "Обновление ОС до Ubuntu 22.04",
                "Массовое обновление серверов, тестирование совместимости сервисов.",
                "UBU",
            ),
            (
                "Реализация VPN для удалённых офисов",
                "Настройка OpenVPN/IPSec для безопасного подключения сотрудников вне офиса.",
                "VPN",
            ),
            (
                "Разработка мобильного приложения",
                "Создание кроссплатформенного мобильного приложения для клиентов.",
                "MOB",
            ),
            (
                "Интеграция с внешними API",
                "Внедрение интеграции с внешними сервисами и API.",
                "API",
            ),
            (
                "Миграция на PostgreSQL",
                "Переезд с MySQL на PostgreSQL, оптимизация запросов.",
                "PGS",
            ),
            ("Внедрение SSO", "Единая точка входа для всех сервисов компании.", "SSO"),
            (
                "Разработка внутреннего портала",
                "Создание корпоративного портала для сотрудников.",
                "INTR",
            ),
        ]
        projects = []
        for idx, (name, description, code) in enumerate(project_templates, start=1):
            proj = Project.objects.create(name=name, description=description, code=code)
            members = random.sample(users, random.randint(3, 5))
            proj.members.set(members)
            proj.save()
            member_names = ", ".join([f"{u.first_name} {u.last_name}" for u in members])
            self.stdout.write(
                f"✓ Project #{idx}: {name} (code: {code}, members: {member_names})"
            )
            projects.append(proj)

        Task.objects.all().delete()
        task_counter = 0
        tasks = []
        task_titles = [
            "Обновить конфигурацию брандмауэра",
            "Деплой нового VPN-сервера",
            "Настроить резервное копирование БД",
            "Проверить логирование ошибок",
            "Оптимизировать SQL-запросы",
            "Перезапустить веб-сервер",
            "Проверить сертификаты SSL",
            "Настроить алерты по CPU",
            "Обновить Docker-образы",
            "Проверить доступность сетевых узлов",
            "Добавить мониторинг памяти",
            "Провести нагрузочное тестирование",
            "Внедрить автоматическое масштабирование",
            "Обновить документацию по проекту",
            "Провести аудит безопасности",
            "Настроить CI для автотестов",
            "Провести ревью кода",
            "Добавить интеграцию с Telegram",
            "Провести миграцию данных",
            "Провести обучение команды",
        ]
        task_comments_pool = [
            "Проверил, всё работает корректно.",
            "Найдено несоответствие в конфигурации, исправляю.",
            "Сервер перезагружен, проблем не выявлено.",
            "Добавил недостающие индексы, производительность выросла.",
            "Ожидается ответ от коллег по поводу прав доступа.",
            "Тестирование прошло успешно, переключаю на рабочую среду.",
            "Найден баг при обновлении, нужна дополнительная проверка.",
            "Контейнеры были сброшены, запускаю задания заново.",
            "Сбой из-за нехватки дискового пространства, устраняю.",
            "Всё готово, закрываю задачу.",
            "Провёл рефакторинг, стало чище.",
            "Добавил логирование ошибок.",
            "Провёл оптимизацию SQL-запросов.",
            "Провёл интеграцию с внешним сервисом.",
            "Провёл обновление зависимостей.",
            "Провёл ревью, замечания отправил.",
            "Провёл тестирование на разных окружениях.",
            "Провёл обновление документации.",
            "Провёл аудит безопасности, критичных проблем нет.",
            "Провёл обучение новых сотрудников.",
        ]

        for proj in projects:
            proj_members = list(proj.members.all())
            num_tasks = random.randint(7, 15)
            used_titles = set()
            for j in range(1, num_tasks + 1):
                title = random.choice(
                    [t for t in task_titles if t not in used_titles] or task_titles
                )
                used_titles.add(title)
                description = (
                    f"Задача по проекту «{proj.name}»: {title}. "
                    f"{random.choice(['Необходимо выполнить в ближайшие сроки.', 'Требуется согласование с командой.', 'Провести тестирование после выполнения.', 'Проконтролировать результат и отчитаться.'])}"
                )
                creator = random.choice(proj_members)
                assignee = random.choice(proj_members)
                status = random.choice(statuses)
                priority = random.choice(priorities)
                due_date = timezone.now() + timezone.timedelta(
                    days=random.randint(1, 30)
                )
                task = Task.objects.create(
                    title=title,
                    description=description,
                    creator=creator,
                    assignee=assignee,
                    project=proj,
                    status=status,
                    priority=priority,
                    due_date=due_date,
                )
                tasks.append(task)
                task_counter += 1
                self.stdout.write(
                    f"  ✓ Task #{task_counter}: {title} "
                    f"(Creator: {creator.first_name} {creator.last_name}, "
                    f"Assignee: {assignee.first_name} {assignee.last_name}, "
                    f"Status: {status.name}, Priority: {priority.level})"
                )

        Comment.objects.all().delete()
        comment_counter = 0

        for t in tasks:
            t_members = list(t.project.members.all())
            num_comments = random.randint(5, 15)
            used_comments = set()
            for k in range(1, num_comments + 1):
                text_template = random.choice(
                    [c for c in task_comments_pool if c not in used_comments]
                    or task_comments_pool
                )
                used_comments.add(text_template)
                text = f"{text_template}"
                author = random.choice(t_members)
                Comment.objects.create(task=t, author=author, text=text)
                comment_counter += 1
            self.stdout.write(
                f"    ✓ Добавлено {num_comments} комментариев к Task #{t.id}"
            )

        self.stdout.write(
            self.style.SUCCESS("✔ Заполнение реальными тестовыми данными завершено!")
        )
