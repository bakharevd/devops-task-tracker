from rest_framework import viewsets, permissions, filters
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Task, Status, Priority, Project, Comment
from .permissions import IsAuthorOrAdmin
from .serializers import (
    TaskSerializer,
    StatusSerializer,
    PrioritySerializer,
    ProjectSerializer
)
from .serializers_comment import CommentSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description', 'members__username']

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return Project.objects.prefetch_related('members').all()
        return Project.objects.filter(members=user).prefetch_related('members')

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), permissions.IsAdminUser()]


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']

    def get_queryset(self):
        user = self.request.user
        qs = Task.objects.select_related('creator', 'assignee', 'status', 'priority', 'project').all()
        project_param = self.request.query_params.get('project')
        if project_param:
            if project_param == 'all':
                pass
            else:
                try:
                    proj_id = int(project_param)
                    qs = qs.filter(project_id=proj_id)
                except (ValueError, TypeError):
                    pass
        if not (user.is_superuser or user.is_staff):
            user_projects = user.projects.all()
            qs = qs.filter(project__in=user_projects)
        return qs

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save()


class StatusViewSet(viewsets.ModelViewSet):
    queryset = Status.objects.all()
    serializer_class = StatusSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), permissions.IsAdminUser()]


class PriorityViewSet(viewsets.ModelViewSet):
    queryset = Priority.objects.all()
    serializer_class = PrioritySerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), permissions.IsAdminUser()]


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related('author', 'task').all()
    serializer_class = CommentSerializer
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['text']

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsAuthorOrAdmin()]

    def get_queryset(self):
        queryset = super().get_queryset()
        task_id = self.request.query_params.get('task')
        if task_id:
            try:
                tid = int(task_id)
                return queryset.filter(task_id=tid)
            except (ValueError, TypeError):
                return queryset
        return queryset
