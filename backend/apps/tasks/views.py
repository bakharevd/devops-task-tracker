from rest_framework import viewsets, permissions, filters
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Task, Status, Priority, Project, Comment
from .permissions import IsAuthorOrAdmin
from .serializers import (
    TaskSerializer,
    StatusSerializer,
    PrioritySerializer,
    ProjectSerializer,
)
from .serializers_comment import CommentSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления проектами.

    Предоставляет CRUD операции для проектов с учетом прав доступа:
    - Просмотр списка проектов и деталей доступен всем аутентифицированным пользователям
    - Создание, изменение и удаление проектов доступно только администраторам
    - Пользователи видят только те проекты, в которых они являются участниками
    """

    serializer_class = ProjectSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "description", "members__username"]

    def get_queryset(self):
        """
        Возвращает queryset проектов с учетом прав доступа пользователя.

        Returns:
            QuerySet: Список проектов, доступных пользователю
        """
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return Project.objects.prefetch_related("members").all()
        return Project.objects.filter(members=user).prefetch_related("members")

    def get_permissions(self):
        """
        Определяет права доступа в зависимости от действия.

        Returns:
            list: Список классов разрешений
        """
        if self.action in ["list", "retrieve"]:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), permissions.IsAdminUser()]


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления задачами.

    Предоставляет CRUD операции для задач с учетом прав доступа:
    - Просмотр списка задач и деталей доступен всем аутентифицированным пользователям
    - Создание задач доступно всем аутентифицированным пользователям
    - Изменение и удаление задач доступно создателю задачи
    - Пользователи видят задачи из проектов, в которых они участвуют
    """

    serializer_class = TaskSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "description"]

    def get_queryset(self):
        """
        Возвращает queryset задач с учетом прав доступа и фильтрации по проекту.

        Returns:
            QuerySet: Список задач, доступных пользователю
        """
        user = self.request.user
        qs = Task.objects.select_related(
            "creator", "assignee", "status", "priority", "project"
        ).all()
        project_param = self.request.query_params.get("project")
        not_project_param = self.request.query_params.get("not_project")
        if project_param:
            if project_param == "all":
                pass
            else:
                try:
                    proj_id = int(project_param)
                    qs = qs.filter(project_id=proj_id)
                except (ValueError, TypeError):
                    pass
        elif not_project_param:
            try:
                proj_id = int(not_project_param)
                qs = qs.exclude(project_id=proj_id)
            except (ValueError, TypeError):
                pass

        status_param = self.request.query_params.get("status")
        not_status_param = self.request.query_params.get("not_status")
        if status_param:
            try:
                status_id = int(status_param)
                qs = qs.filter(status_id=status_id)
            except (ValueError, TypeError):
                pass
        elif not_status_param:
            try:
                status_id = int(not_status_param)
                qs = qs.exclude(status_id=status_id)
            except (ValueError, TypeError):
                pass

        assignee_param = self.request.query_params.get("assignee")
        not_assignee_param = self.request.query_params.get("not_assignee")
        if assignee_param:
            try:
                assignee_id = int(assignee_param)
                qs = qs.filter(assignee_id=assignee_id)
            except (ValueError, TypeError):
                pass
        elif not_assignee_param:
            try:
                assignee_id = int(not_assignee_param)
                qs = qs.exclude(assignee_id=assignee_id)
            except (ValueError, TypeError):
                pass

        if self.request.query_params.get("unassigned") == "true":
            qs = qs.filter(assignee__isnull=True)

        if not (user.is_superuser or user.is_staff):
            qs = qs.filter(project__members=user) | qs.filter(creator=user)
        return qs

    def get_object(self):
        """
        Получает объект задачи по ID или issue_id.

        Returns:
            Task: Объект задачи
        """
        by_issue_id = self.request.query_params.get("by_issue_id")
        if by_issue_id:
            issue_id = self.kwargs.get("pk")
            obj = get_object_or_404(Task, issue_id=issue_id)
            self.check_object_permissions(self.request, obj)
            return obj
        return super().get_object()

    def update(self, request, *args, **kwargs):
        """
        Обновляет задачу с учетом возможности обновления по issue_id.

        Args:
            request: HTTP запрос
            *args: Дополнительные аргументы
            **kwargs: Дополнительные именованные аргументы

        Returns:
            Response: Ответ с обновленными данными задачи
        """
        mutable_data = request.data.copy()
        by_issue_id = request.query_params.get("by_issue_id")
        if by_issue_id:
            partial = kwargs.pop("partial", False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=mutable_data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        return super().update(request._request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Удаляет задачу с учетом возможности удаления по issue_id.

        Args:
            request: HTTP запрос
            *args: Дополнительные аргументы
            **kwargs: Дополнительные именованные аргументы

        Returns:
            Response: Пустой ответ со статусом 204
        """
        by_issue_id = request.query_params.get("by_issue_id")
        if by_issue_id:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return super().destroy(request, *args, **kwargs)

    def get_permissions(self):
        """
        Определяет права доступа в зависимости от действия.

        Returns:
            list: Список классов разрешений
        """
        if self.action in ["list", "retrieve", "create"]:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        """
        Создает новую задачу.

        Args:
            serializer: Сериализатор с данными задачи
        """
        serializer.save()


class StatusViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления статусами задач.

    Предоставляет CRUD операции для статусов с учетом прав доступа:
    - Просмотр списка статусов и деталей доступен всем аутентифицированным пользователям
    - Создание, изменение и удаление статусов доступно только администраторам
    """

    queryset = Status.objects.all()
    serializer_class = StatusSerializer

    def get_permissions(self):
        """
        Определяет права доступа в зависимости от действия.

        Returns:
            list: Список классов разрешений
        """
        if self.action in ["list", "retrieve"]:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), permissions.IsAdminUser()]


class PriorityViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления приоритетами задач.

    Предоставляет CRUD операции для приоритетов с учетом прав доступа:
    - Просмотр списка приоритетов и деталей доступен всем аутентифицированным пользователям
    - Создание, изменение и удаление приоритетов доступно только администраторам
    """

    queryset = Priority.objects.all()
    serializer_class = PrioritySerializer

    def get_permissions(self):
        """
        Определяет права доступа в зависимости от действия.

        Returns:
            list: Список классов разрешений
        """
        if self.action in ["list", "retrieve"]:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), permissions.IsAdminUser()]


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления комментариями к задачам.

    Предоставляет CRUD операции для комментариев с учетом прав доступа:
    - Просмотр списка комментариев, деталей и создание доступно всем аутентифицированным пользователям
    - Изменение и удаление комментариев доступно только автору комментария или администратору
    - Поддерживает загрузку файлов в комментариях
    """

    queryset = Comment.objects.select_related("author", "task").all()
    serializer_class = CommentSerializer
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [filters.SearchFilter]
    search_fields = ["text"]

    def get_permissions(self):
        """
        Определяет права доступа в зависимости от действия.

        Returns:
            list: Список классов разрешений
        """
        if self.action in ["list", "retrieve", "create"]:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsAuthorOrAdmin()]

    def get_queryset(self):
        """
        Возвращает queryset комментариев с учетом фильтрации по задаче.

        Returns:
            QuerySet: Список комментариев, отфильтрованных по параметрам запроса
        """
        queryset = super().get_queryset()
        task_id = self.request.query_params.get("task")
        task_issue_id = self.request.query_params.get("task_issue_id")
        if task_issue_id:
            return queryset.filter(task__issue_id=task_issue_id)
        if task_id:
            try:
                tid = int(task_id)
                return queryset.filter(task_id=tid)
            except (ValueError, TypeError):
                return queryset
        return queryset
