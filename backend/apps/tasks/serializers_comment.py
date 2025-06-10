from rest_framework import serializers

from .models import Comment, Task
from ..users.serializers import UserSerializer


class CommentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Comment.

    Предоставляет сериализацию и десериализацию комментариев с учетом:
    - Чтения автора комментария через UserSerializer
    - Чтения задачи в режиме только для чтения
    - Записи задачи через ID или issue_id
    - Поддержки загрузки файлов в качестве вложений
    - Автоматического назначения текущего пользователя автором при создании
    """

    author = UserSerializer(read_only=True)
    task = serializers.PrimaryKeyRelatedField(read_only=True)
    task_id = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all(), write_only=True, source="task", required=False
    )
    attachment = serializers.FileField(required=False, allow_null=True)
    task_issue_id = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Comment
        fields = [
            "id",
            "task",
            "task_id",
            "author",
            "text",
            "attachment",
            "created_at",
            "updated_at",
            "task_issue_id",
        ]
        read_only_fields = ["id", "author", "created_at", "updated_at", "task"]

    def validate(self, attrs):
        """
        Проверяет, что указан либо task_id, либо task_issue_id.

        Args:
            attrs (dict): Валидируемые атрибуты

        Returns:
            dict: Валидированные атрибуты

        Raises:
            serializers.ValidationError: Если не указан ни task_id, ни task_issue_id
        """
        if not attrs.get("task") and not self.initial_data.get("task_issue_id"):
            raise serializers.ValidationError(
                "Необходимо указать task_id или task_issue_id"
            )
        return attrs

    def create(self, validated_data):
        """
        Создает новый комментарий, автоматически назначая текущего пользователя автором
        и обрабатывая task_issue_id, если он указан.

        Args:
            validated_data (dict): Валидированные данные для создания комментария

        Returns:
            Comment: Созданный комментарий
        """
        request = self.context.get("request", None)
        task_issue_id = validated_data.pop("task_issue_id", None)
        if task_issue_id:
            task = Task.objects.get(issue_id=task_issue_id)
            validated_data["task"] = task
        if request and hasattr(request, "user"):
            validated_data["author"] = request.user
        return super().create(validated_data)
