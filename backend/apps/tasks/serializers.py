from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Task, Status, Priority, Project
from ..users.serializers import UserSerializer

User = get_user_model()


class ProjectSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Project.

    Предоставляет сериализацию и десериализацию проектов с учетом:
    - Чтения списка участников проекта через UserSerializer
    - Записи участников проекта через список ID пользователей
    """

    members = UserSerializer(read_only=True, many=True)
    members_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, write_only=True, source="members"
    )

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "code",
            "description",
            "created_at",
            "updated_at",
            "members",
            "members_ids",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        """
        Создает новый проект и устанавливает его участников.

        Args:
            validated_data (dict): Валидированные данные для создания проекта

        Returns:
            Project: Созданный проект
        """
        members = validated_data.pop("members", [])
        project = Project.objects.create(**validated_data)
        project.members.set(members)
        return project

    def update(self, instance, validated_data):
        """
        Обновляет существующий проект и его участников.

        Args:
            instance (Project): Обновляемый проект
            validated_data (dict): Валидированные данные для обновления

        Returns:
            Project: Обновленный проект
        """
        members = validated_data.pop("members", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if members is not None:
            instance.members.set(members)
        return instance


class StatusSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Status.

    Предоставляет сериализацию и десериализацию статусов задач.
    """

    class Meta:
        model = Status
        fields = ["id", "name"]


class PrioritySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Priority.

    Предоставляет сериализацию и десериализацию приоритетов задач.
    """

    class Meta:
        model = Priority
        fields = ["id", "level"]


class TaskSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Task.

    Предоставляет сериализацию и десериализацию задач с учетом:
    - Чтения создателя, исполнителя и проекта через соответствующие сериализаторы
    - Записи создателя, исполнителя и проекта через их ID
    - Автоматического назначения текущего пользователя создателем при создании задачи
    """

    creator = UserSerializer(read_only=True)
    creator_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="creator", write_only=True, required=False
    )

    assignee = UserSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="assignee",
        write_only=True,
        allow_null=True,
        required=False,
    )

    project = ProjectSerializer(read_only=True)
    project_id = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), write_only=True, source="project", required=True
    )
    status = serializers.PrimaryKeyRelatedField(queryset=Status.objects.all())
    priority = serializers.PrimaryKeyRelatedField(queryset=Priority.objects.all())
    issue_id = serializers.CharField(read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "issue_id",
            "title",
            "description",
            "created_at",
            "updated_at",
            "due_date",
            "creator",
            "creator_id",
            "assignee",
            "assignee_id",
            "project",
            "project_id",
            "status",
            "priority",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "creator",
            "project",
            "assignee",
            "issue_id",
        ]

    def create(self, validated_data):
        """
        Создает новую задачу, автоматически назначая текущего пользователя создателем,
        если создатель не указан явно.

        Args:
            validated_data (dict): Валидированные данные для создания задачи

        Returns:
            Task: Созданная задача
        """
        request = self.context.get("request", None)
        if request and hasattr(request, "user") and "creator" not in validated_data:
            validated_data["creator"] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Обновляет существующую задачу.

        Args:
            instance (Task): Обновляемая задача
            validated_data (dict): Валидированные данные для обновления

        Returns:
            Task: Обновленная задача
        """
        return super().update(instance, validated_data)
