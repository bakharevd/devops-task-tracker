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
    serializer_class = ProjectSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "description", "members__username"]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return Project.objects.prefetch_related("members").all()
        return Project.objects.filter(members=user).prefetch_related("members")

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), permissions.IsAdminUser()]


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "description"]

    def get_queryset(self):
        user = self.request.user
        qs = Task.objects.select_related(
            "creator", "assignee", "status", "priority", "project"
        ).all()
        project_param = self.request.query_params.get("project")
        if project_param:
            if project_param == "all":
                pass
            else:
                try:
                    proj_id = int(project_param)
                    qs = qs.filter(project_id=proj_id)
                except (ValueError, TypeError):
                    pass
        if not (user.is_superuser or user.is_staff):
            qs = qs.filter(project__members=user) | qs.filter(creator=user)
        return qs

    def get_object(self):
        by_issue_id = self.request.query_params.get("by_issue_id")
        if by_issue_id:
            issue_id = self.kwargs.get("pk")
            obj = get_object_or_404(Task, issue_id=issue_id)
            self.check_object_permissions(self.request, obj)
            return obj
        return super().get_object()

    def update(self, request, *args, **kwargs):
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
        by_issue_id = request.query_params.get("by_issue_id")
        if by_issue_id:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return super().destroy(request, *args, **kwargs)

    def get_permissions(self):
        if self.action in ["list", "retrieve", "create"]:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save()


class StatusViewSet(viewsets.ModelViewSet):
    queryset = Status.objects.all()
    serializer_class = StatusSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), permissions.IsAdminUser()]


class PriorityViewSet(viewsets.ModelViewSet):
    queryset = Priority.objects.all()
    serializer_class = PrioritySerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), permissions.IsAdminUser()]


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related("author", "task").all()
    serializer_class = CommentSerializer
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [filters.SearchFilter]
    search_fields = ["text"]

    def get_permissions(self):
        if self.action in ["list", "retrieve", "create"]:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsAuthorOrAdmin()]

    def get_queryset(self):
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
