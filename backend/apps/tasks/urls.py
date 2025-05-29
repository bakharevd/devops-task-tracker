from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TaskViewSet, StatusViewSet, PriorityViewSet

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='tasks')
router.register(r'statuses', StatusViewSet, basename='statuses')
router.register(r'priorities', PriorityViewSet, basename='priorities')

urlpatterns = [
    path('', include(router.urls)),
]
