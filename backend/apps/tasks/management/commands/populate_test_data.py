import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.users.models import Position
from ...models import Status, Priority, Project, Task, Comment

User = get_user_model()

TRANSLIT_DICT = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
    'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i',
    'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
    'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
    'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch',
    'ш': 'sh', 'щ': 'shch', 'ъ': '', 'ы': 'y', 'ь': '',
    'э': 'e', 'ю': 'yu', 'я': 'ya',

    # заглавные
    'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D',
    'Е': 'E', 'Ё': 'Yo', 'Ж': 'Zh', 'З': 'Z', 'И': 'I',
    'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N',
    'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T',
    'У': 'U', 'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch',
    'Ш': 'Sh', 'Щ': 'Shch', 'Ъ': '', 'Ы': 'Y', 'Ь': '',
    'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
}


def transliterate(text: str) -> str:
    return ''.join(TRANSLIT_DICT.get(char, char) for char in text)


class Command(BaseCommand):
    help = (
        "Заполняет БД реалистичными тестовыми данными:\n"
        "• 5 позиций (Position)\n"
        "• 10 пользователей (User) с паролем 'Kief22Mo'\n"
        "• 5 статусов (Status)\n"
        "• 5 приоритетов (Priority)\n"
        "• 10 проектов (Project) с 3–5 участниками\n"
        "• 10 задач (Task) на каждый проект"
        "• 10 комментариев (Comment) на каждую задачу\n\n"
        "Запуск:\n  python manage.py populate_test_data\n"
        "В Docker:\n  docker-compose exec backend python manage.py populate_test_data"
    )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Старт заполнения реалистичными данными..."))

        Position.objects.all().delete()
        pos_names = [
            "DevOps Engineer",
            "System Administrator",
            "Network Engineer",
            "Support Specialist",
            "Cloud Architect"
        ]
        positions = []
        for name in pos_names:
            pos = Position.objects.create(name=name)
            positions.append(pos)
            self.stdout.write(f"✓ Position: {name}")

        User.objects.all().delete()
        user_data = [
            ("Алексей", "Иванов"),
            ("Мария", "Петрова"),
            ("Дмитрий", "Соколов"),
            ("Екатерина", "Кузнецова"),
            ("Игорь", "Васильев"),
            ("Ольга", "Смирнова"),
            ("Сергей", "Попов"),
            ("Анна", "Николаева"),
            ("Владимир", "Морозов"),
            ("Юлия", "Лебедева")
        ]
        from django.contrib.auth.hashers import make_password
        hashed_pw = make_password("Kief22Mo")

        users = []
        for idx, (first, last) in enumerate(user_data, start=1):
            username = f"{transliterate(first.lower())[0]}.{transliterate(last.lower())}"
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
                is_active=True
            )
            user.save()
            users.append(user)
            self.stdout.write(f"✓ User #{idx}: {first} {last}, position={position.name}")

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
            ("Миграция на AWS", "Перенос инфраструктуры в облако AWS: контейнеризация, Terraform, настройка CI/CD."),
            ("Внедрение мониторинга",
             "Установка и настройка Prometheus/Grafana для отслеживания производительности серверов."),
            ("Обновление сетевой инфраструктуры", "Замена устаревшего оборудования, настройка VLAN и QoS."),
            ("Резервное копирование и DR", "Организация регулярного бэкапа баз данных, настройка DR-плана."),
            ("Переход на Kubernetes", "Перенос микросервисов в k8s-кластер, настройка Helm-чартов."),
            ("SSL и безопасность", "Установка Let's Encrypt, настройка WAF и сканирование уязвимостей."),
            ("Внедрение CI/CD", "Настройка GitLab CI для проекта, автоматизация деплоя и тестирования."),
            ("Оптимизация БД", "Ревизия индексов, настройка репликации, оптимизация SQL-запросов."),
            ("Обновление ОС до Ubuntu 22.04", "Массовое обновление серверов, тестирование совместимости сервисов."),
            ("Реализация VPN для удалённых офисов",
             "Настройка OpenVPN/IPSec для безопасного подключения сотрудников вне офиса.")
        ]
        projects = []
        for idx, (name, description) in enumerate(project_templates, start=1):
            proj = Project.objects.create(name=name, description=description)
            members = random.sample(users, random.randint(3, 5))
            proj.members.set(members)
            proj.save()
            member_names = ", ".join([f"{u.first_name} {u.last_name}" for u in members])
            self.stdout.write(f"✓ Project #{idx}: {name} (members: {member_names})")
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
            "Проверить доступность сетевых узлов"
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
            "Всё готово, закрываю задачу."
        ]

        for proj in projects:
            proj_members = list(proj.members.all())
            for j in range(1, 11):
                title = random.choice(task_titles)
                description = (
                    f"Задача по проекту «{proj.name}»: {title}. "
                    "Необходимо выполнить в ближайшие сроки и уведомить команду."
                )
                creator = random.choice(proj_members)
                assignee = random.choice(proj_members)
                status = random.choice(statuses)
                priority = random.choice(priorities)
                due_date = timezone.now() + timezone.timedelta(days=random.randint(1, 30))
                task = Task.objects.create(
                    title=title,
                    description=description,
                    creator=creator,
                    assignee=assignee,
                    project=proj,
                    status=status,
                    priority=priority,
                    due_date=due_date
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
            for k in range(1, 11):
                text_template = random.choice(task_comments_pool)
                text = (
                    f"{text_template}"
                )
                author = random.choice(t_members)
                Comment.objects.create(
                    task=t,
                    author=author,
                    text=text
                )
                comment_counter += 1
            self.stdout.write(f"    ✓ Добавлено 10 комментариев к Task #{t.id}")

        self.stdout.write(self.style.SUCCESS("✔ Заполнение реальными тестовыми данными завершено!"))
