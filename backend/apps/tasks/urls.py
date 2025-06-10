from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    TaskViewSet,
    StatusViewSet,
    PriorityViewSet,
    ProjectViewSet,
    CommentViewSet,
)

router = DefaultRouter()
router.register(r"projects", ProjectViewSet, basename="projects")
router.register(r"tasks", TaskViewSet, basename="tasks")
router.register(r"statuses", StatusViewSet, basename="statuses")
router.register(r"priorities", PriorityViewSet, basename="priorities")
router.register(r"comments", CommentViewSet, basename="comments")

urlpatterns = [
    path("", include(router.urls)),
]
