import pytest
from django.urls import reverse
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate
from django.contrib.auth import get_user_model
from django.core.management import call_command
from rest_framework import status as drf_status
from apps.tasks.models import Project, Task, Status, Priority, Comment
from apps.tasks.management.commands.populate_test_data import Command as PopulateCommand
from apps.tasks.serializers import (
    TaskSerializer,
    ProjectSerializer,
    StatusSerializer,
    PrioritySerializer,
)
from apps.tasks.serializers_comment import CommentSerializer
from apps.tasks.views import (
    TaskViewSet,
    CommentViewSet,
    ProjectViewSet,
    StatusViewSet,
    PriorityViewSet,
)
from apps.tasks.permissions import IsAuthorOrAdmin
from django.db import IntegrityError

User = get_user_model()


@pytest.mark.django_db
def test_project_code_uppercase():
    project = Project.objects.create(name="Test Project", code="abc")
    assert project.code == "ABC"


@pytest.mark.django_db
def test_status_and_priority_str():
    status = Status.objects.create(name="Test Status")
    priority = Priority.objects.create(level="Test Priority")
    assert str(status) == "Test Status"
    assert str(priority) == "Test Priority"


@pytest.mark.django_db
def test_task_issue_id_and_str():
    project = Project.objects.create(name="Test Project", code="prj")
    status = Status.objects.create(name="Open")
    priority = Priority.objects.create(level="Low")
    user = User.objects.create(username="user1", email="u1@test.com")
    task = Task.objects.create(
        title="Test Task",
        project=project,
        status=status,
        priority=priority,
        creator=user,
    )
    assert task.issue_id == "PRJ-1"
    assert str(task).startswith("Test Task (")


@pytest.mark.django_db
def test_comment_str():
    project = Project.objects.create(name="Test Project", code="PRJ")
    status = Status.objects.create(name="Open")
    priority = Priority.objects.create(level="Low")
    user = User.objects.create(username="user1", email="u1@test.com")
    task = Task.objects.create(
        title="Test Task",
        project=project,
        status=status,
        priority=priority,
        creator=user,
    )
    comment = Comment.objects.create(task=task, author=user, text="Test comment")
    assert str(comment).startswith("Комментарий #")


@pytest.mark.django_db
def test_task_serializer_create_and_update():
    project = Project.objects.create(name="Test Project", code="PRJ")
    project2 = Project.objects.create(name="Test Project 2", code="PRJ2")
    status = Status.objects.create(name="Open")
    priority = Priority.objects.create(level="Low")
    user1 = User.objects.create(username="user1", email="u1@test.com")
    user2 = User.objects.create(username="user2", email="u2@test.com")
    data = {
        "title": "Task S1",
        "description": "desc",
        "project_id": project.id,
        "status": status.id,
        "priority": priority.id,
        "creator_id": user1.id,
        "assignee_id": user2.id,
    }
    serializer = TaskSerializer(data=data)
    assert serializer.is_valid(), serializer.errors
    task = serializer.save()
    assert task.project == project
    assert task.assignee == user2
    update_data = {"title": "Task S1 updated", "project_id": project2.id}
    serializer = TaskSerializer(task, data=update_data, partial=True)
    assert serializer.is_valid(), serializer.errors
    updated_task = serializer.save()
    assert updated_task.project == project2


@pytest.mark.django_db
def test_task_viewset_crud():
    factory = APIRequestFactory()
    user = User.objects.create(username="user1", email="u1@test.com")
    project = Project.objects.create(name="Test Project", code="PRJ")
    status = Status.objects.create(name="Open")
    priority = Priority.objects.create(level="Low")
    data = {
        "title": "Task V1",
        "description": "desc",
        "project_id": project.id,
        "status": status.id,
        "priority": priority.id,
        "creator_id": user.id,
    }
    view = TaskViewSet.as_view({"post": "create"})
    request = factory.post("/tasks/", data)
    force_authenticate(request, user=user)
    response = view(request)
    assert response.status_code == 201
    task_id = response.data["id"]
    issue_id = response.data["issue_id"]
    view = TaskViewSet.as_view({"get": "retrieve"})
    request = factory.get(f"/tasks/{task_id}/")
    force_authenticate(request, user=user)
    response = view(request, pk=task_id)
    assert response.status_code == 200
    request = factory.get(f"/tasks/{issue_id}/?by_issue_id=1")
    force_authenticate(request, user=user)
    response = view(request, pk=issue_id)
    assert response.status_code == 200
    view = TaskViewSet.as_view({"patch": "partial_update"})
    request = factory.patch(
        f"/tasks/{issue_id}/?by_issue_id=1",
        {"title": "Updated"},
        content_type="application/json",
    )
    force_authenticate(request, user=user)
    response = view(request, pk=issue_id)
    assert response.status_code == 200
    view = TaskViewSet.as_view({"delete": "destroy"})
    request = factory.delete(f"/tasks/{issue_id}/?by_issue_id=1")
    force_authenticate(request, user=user)
    response = view(request, pk=issue_id)
    assert response.status_code == 204


@pytest.mark.django_db
def test_comment_viewset_crud():
    factory = APIRequestFactory()
    user = User.objects.create(username="user1", email="u1@test.com")
    project = Project.objects.create(name="Test Project", code="PRJ")
    status = Status.objects.create(name="Open")
    priority = Priority.objects.create(level="Low")
    task = Task.objects.create(
        title="Task", project=project, status=status, priority=priority, creator=user
    )
    data = {"task_id": task.id, "text": "Comment 1"}
    view = CommentViewSet.as_view({"post": "create"})
    request = factory.post("/comments/", data)
    force_authenticate(request, user=user)
    response = view(request)
    assert response.status_code == 201
    comment_id = response.data["id"]
    view = CommentViewSet.as_view({"get": "list"})
    request = factory.get(f"/comments/?task={task.id}")
    force_authenticate(request, user=user)
    response = view(request)
    assert response.status_code == 200
    request = factory.get(f"/comments/?task_issue_id={task.issue_id}")
    force_authenticate(request, user=user)
    response = view(request)
    assert response.status_code == 200
    view = CommentViewSet.as_view({"delete": "destroy"})
    request = factory.delete(f"/comments/{comment_id}/")
    force_authenticate(request, user=user)
    response = view(request, pk=comment_id)
    assert response.status_code == 204


@pytest.mark.django_db
def test_populate_test_data_command():
    call_command("populate_test_data")
    assert Project.objects.count() > 0
    assert Task.objects.count() > 0
    assert Comment.objects.count() > 0
    assert User.objects.filter(email="s@bhrv.dev").exists()


@pytest.mark.django_db
def test_project_viewset_crud_and_permissions():
    factory = APIRequestFactory()
    user = User.objects.create(username="user1", email="u1@test.com")
    admin = User.objects.create(
        username="admin", email="admin@test.com", is_superuser=True, is_staff=True
    )
    data = {"name": "Project1", "code": "p1", "members_ids": [admin.id]}
    view = ProjectViewSet.as_view({"post": "create"})
    request = factory.post("/projects/", data)
    force_authenticate(request, user=admin)
    response = view(request)
    assert response.status_code == 201
    project_id = response.data["id"]
    view = ProjectViewSet.as_view({"get": "list"})
    request = factory.get("/projects/")
    force_authenticate(request, user=user)
    response = view(request)
    assert response.status_code == 200
    view = ProjectViewSet.as_view({"get": "retrieve"})
    request = factory.get(f"/projects/{project_id}/")
    force_authenticate(request, user=admin)
    response = view(request, pk=project_id)
    assert response.status_code == 200
    view = ProjectViewSet.as_view({"put": "update"})
    request = factory.put(
        f"/projects/{project_id}/",
        {"name": "Project1-upd", "code": "P1UPD", "members_ids": [admin.id]},
        content_type="application/json",
    )
    force_authenticate(request, user=admin)
    response = view(request, pk=project_id)
    if response.status_code != 200:
        print(f"Validation errors: {response.data}")
    assert response.status_code == 200
    view = ProjectViewSet.as_view({"delete": "destroy"})
    request = factory.delete(f"/projects/{project_id}/")
    force_authenticate(request, user=admin)
    response = view(request, pk=project_id)
    assert response.status_code == 204
    view = ProjectViewSet.as_view({"post": "create"})
    request = factory.post("/projects/", {"name": "P2", "code": "P2"})
    force_authenticate(request, user=user)
    response = view(request)
    assert response.status_code == drf_status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_status_priority_viewset_crud():
    factory = APIRequestFactory()
    admin = User.objects.create(
        username="admin", email="admin@test.com", is_superuser=True, is_staff=True
    )
    view = StatusViewSet.as_view({"post": "create"})
    request = factory.post("/statuses/", {"name": "St1"})
    force_authenticate(request, user=admin)
    response = view(request)
    assert response.status_code == 201
    status_id = response.data["id"]
    view = PriorityViewSet.as_view({"post": "create"})
    request = factory.post("/priorities/", {"level": "High"})
    force_authenticate(request, user=admin)
    response = view(request)
    assert response.status_code == 201
    priority_id = response.data["id"]
    view = StatusViewSet.as_view({"get": "list"})
    request = factory.get("/statuses/")
    force_authenticate(request, user=admin)
    response = view(request)
    assert response.status_code == 200
    view = StatusViewSet.as_view({"put": "update"})
    request = factory.put(
        f"/statuses/{status_id}/", {"name": "St1-upd"}, content_type="application/json"
    )
    force_authenticate(request, user=admin)
    response = view(request, pk=status_id)
    assert response.status_code == 200
    view = StatusViewSet.as_view({"delete": "destroy"})
    request = factory.delete(f"/statuses/{status_id}/")
    force_authenticate(request, user=admin)
    response = view(request, pk=status_id)
    assert response.status_code == 204


@pytest.mark.django_db
def test_comment_permissions_and_errors():
    factory = APIRequestFactory()
    user1 = User.objects.create(username="user1", email="u1@test.com")
    user2 = User.objects.create(username="user2", email="u2@test.com")
    project = Project.objects.create(name="Test Project", code="PRJ")
    status = Status.objects.create(name="Open")
    priority = Priority.objects.create(level="Low")
    task = Task.objects.create(
        title="Task", project=project, status=status, priority=priority, creator=user1
    )
    data = {"task_id": task.id, "text": "Comment 1"}
    view = CommentViewSet.as_view({"post": "create"})
    request = factory.post("/comments/", data)
    force_authenticate(request, user=user1)
    response = view(request)
    assert response.status_code == 201
    comment_id = response.data["id"]
    view = CommentViewSet.as_view({"delete": "destroy"})
    request = factory.delete(f"/comments/{comment_id}/")
    force_authenticate(request, user=user2)
    response = view(request, pk=comment_id)
    assert response.status_code == drf_status.HTTP_403_FORBIDDEN
    view = CommentViewSet.as_view({"post": "create"})
    request = factory.post("/comments/", {"task_id": task.id})
    force_authenticate(request, user=user1)
    response = view(request)
    assert response.status_code == drf_status.HTTP_400_BAD_REQUEST
    view = CommentViewSet.as_view({"post": "create"})
    request = factory.post("/comments/", {"task_id": task.id, "text": "C2"})
    response = view(request)
    assert response.status_code == drf_status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_project_serializer_create_and_update():
    user1 = User.objects.create(username="user1", email="u1@test.com")
    user2 = User.objects.create(username="user2", email="u2@test.com")
    data = {"name": "Proj", "code": "abc", "members_ids": [user1.id, user2.id]}
    serializer = ProjectSerializer(data=data)
    assert serializer.is_valid(), serializer.errors
    project = serializer.save()
    assert project.code == "ABC"
    assert user1 in project.members.all()
    update_data = {"name": "Proj2", "members_ids": [user1.id]}
    serializer = ProjectSerializer(project, data=update_data, partial=True)
    assert serializer.is_valid(), serializer.errors
    updated = serializer.save()
    assert updated.name == "Proj2"
    assert user2 not in updated.members.all()


@pytest.mark.django_db
def test_status_priority_serializer():
    s = StatusSerializer(data={"name": "St"})
    assert s.is_valid()
    s.save()
    p = PrioritySerializer(data={"level": "High"})
    assert p.is_valid()
    p.save()
    s2 = StatusSerializer(data={})
    assert not s2.is_valid()
    p2 = PrioritySerializer(data={})
    assert not p2.is_valid()


@pytest.mark.django_db
def test_comment_serializer_create_and_errors():
    user = User.objects.create(username="user1", email="u1@test.com")
    project = Project.objects.create(name="Test Project", code="PRJ")
    status = Status.objects.create(name="Open")
    priority = Priority.objects.create(level="Low")
    task = Task.objects.create(
        title="Task", project=project, status=status, priority=priority, creator=user
    )
    data = {"task_id": task.id, "text": "Comment"}
    serializer = CommentSerializer(
        data=data, context={"request": type("obj", (), {"user": user})()}
    )
    assert serializer.is_valid(), serializer.errors
    comment = serializer.save()
    assert comment.text == "Comment"
    serializer = CommentSerializer(
        data={"task_id": task.id},
        context={"request": type("obj", (), {"user": user})()},
    )
    assert not serializer.is_valid()
    serializer = CommentSerializer(
        data={"task_id": 9999, "text": "C"},
        context={"request": type("obj", (), {"user": user})()},
    )
    assert not serializer.is_valid()


@pytest.mark.django_db
def test_is_author_or_admin_permission():
    user = User.objects.create(username="user1", email="u1@test.com")
    admin = User.objects.create(
        username="admin", email="admin@test.com", is_superuser=True
    )
    project = Project.objects.create(name="Test Project", code="PRJ")
    status = Status.objects.create(name="Open")
    priority = Priority.objects.create(level="Low")
    task = Task.objects.create(
        title="Task", project=project, status=status, priority=priority, creator=user
    )
    comment = Comment.objects.create(task=task, author=user, text="C")
    perm = IsAuthorOrAdmin()
    request = type("obj", (), {"user": user})()
    assert perm.has_object_permission(request, None, comment)
    request = type("obj", (), {"user": admin})()
    assert perm.has_object_permission(request, None, comment)
    user2 = User.objects.create(username="user2", email="u2@test.com")
    request = type("obj", (), {"user": user2})()
    assert not perm.has_object_permission(request, None, comment)


@pytest.mark.django_db
def test_task_viewset_errors():
    factory = APIRequestFactory()
    user = User.objects.create(username="user1", email="u1@test.com")
    view = TaskViewSet.as_view({"get": "retrieve"})
    request = factory.get("/tasks/9999/")
    force_authenticate(request, user=user)
    response = view(request, pk=9999)
    assert response.status_code == 404
    view = TaskViewSet.as_view({"post": "create"})
    request = factory.post("/tasks/", {"title": "T"})
    force_authenticate(request, user=user)
    response = view(request)
    assert response.status_code == 400


@pytest.mark.django_db
def test_comment_viewset_errors():
    factory = APIRequestFactory()
    user = User.objects.create(username="user1", email="u1@test.com")
    view = CommentViewSet.as_view({"get": "retrieve"})
    request = factory.get("/comments/9999/")
    force_authenticate(request, user=user)
    response = view(request, pk=9999)
    assert response.status_code == 404
    view = CommentViewSet.as_view({"post": "create"})
    request = factory.post("/comments/", {"text": "C"})
    force_authenticate(request, user=user)
    response = view(request)
    assert response.status_code == 400


@pytest.mark.django_db
def test_task_viewset_by_issue_id():
    factory = APIRequestFactory()
    user = User.objects.create(username="user1", email="u1@test.com")
    project = Project.objects.create(name="Test Project", code="PRJ")
    status = Status.objects.create(name="Open")
    priority = Priority.objects.create(level="Low")
    task = Task.objects.create(
        title="Task V1",
        description="desc",
        project=project,
        status=status,
        priority=priority,
        creator=user,
    )
    view = TaskViewSet.as_view({"get": "retrieve"})
    request = factory.get(f"/tasks/{task.issue_id}/?by_issue_id=1")
    force_authenticate(request, user=user)
    response = view(request, pk=task.issue_id)
    assert response.status_code == 200
    view = TaskViewSet.as_view({"patch": "partial_update"})
    request = factory.patch(
        f"/tasks/{task.issue_id}/?by_issue_id=1",
        {"title": "Updated Task"},
        content_type="application/json",
    )
    force_authenticate(request, user=user)
    response = view(request, pk=task.issue_id)
    assert response.status_code == 200
    view = TaskViewSet.as_view({"delete": "destroy"})
    request = factory.delete(f"/tasks/{task.issue_id}/?by_issue_id=1")
    force_authenticate(request, user=user)
    response = view(request, pk=task.issue_id)
    assert response.status_code == 204


@pytest.mark.django_db
def test_task_viewset_project_filter():
    factory = APIRequestFactory()
    user = User.objects.create(username="user1", email="u1@test.com")
    project1 = Project.objects.create(name="Project 1", code="PRJ1")
    project2 = Project.objects.create(name="Project 2", code="PRJ2")
    status = Status.objects.create(name="Open")
    priority = Priority.objects.create(level="Low")
    task1 = Task.objects.create(
        title="Task 1", project=project1, status=status, priority=priority, creator=user
    )
    task2 = Task.objects.create(
        title="Task 2", project=project2, status=status, priority=priority, creator=user
    )
    view = TaskViewSet.as_view({"get": "list"})
    request = factory.get(f"/tasks/?project={project1.id}")
    force_authenticate(request, user=user)
    response = view(request)
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["id"] == task1.id


@pytest.mark.django_db
def test_comment_viewset_task_issue_id():
    factory = APIRequestFactory()
    user = User.objects.create(username="user1", email="u1@test.com")
    project = Project.objects.create(name="Test Project", code="PRJ")
    status = Status.objects.create(name="Open")
    priority = Priority.objects.create(level="Low")
    task = Task.objects.create(
        title="Task", project=project, status=status, priority=priority, creator=user
    )
    comment = Comment.objects.create(task=task, author=user, text="Test comment")
    view = CommentViewSet.as_view({"get": "list"})
    request = factory.get(f"/comments/?task_issue_id={task.issue_id}")
    force_authenticate(request, user=user)
    response = view(request)
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["id"] == comment.id


@pytest.mark.django_db
def test_task_save_with_existing_issue_id():
    project = Project.objects.create(name="Test Project", code="PRJ")
    status = Status.objects.create(name="Open")
    priority = Priority.objects.create(level="Low")
    user = User.objects.create(username="user1", email="u1@test.com")
    task = Task.objects.create(
        title="Task 1",
        project=project,
        status=status,
        priority=priority,
        creator=user,
        issue_id="PRJ-1",
    )
    task2 = Task.objects.create(
        title="Task 2", project=project, status=status, priority=priority, creator=user
    )
    assert task2.issue_id == "PRJ-2"


@pytest.mark.django_db
def test_task_save_with_invalid_issue_id():
    project = Project.objects.create(name="Test Project", code="PRJ")
    status = Status.objects.create(name="Open")
    priority = Priority.objects.create(level="Low")
    user = User.objects.create(username="user1", email="u1@test.com")
    task = Task.objects.create(
        title="Task 1",
        project=project,
        status=status,
        priority=priority,
        creator=user,
        issue_id="invalid",
    )
    task2 = Task.objects.create(
        title="Task 2", project=project, status=status, priority=priority, creator=user
    )
    assert task2.issue_id == "PRJ-1"


@pytest.mark.django_db
def test_project_save_without_code():
    project = Project(name="NoCodeProject")
    project.save()
    assert project.code is None or project.code == ""


@pytest.mark.django_db
def test_task_save_with_unparsable_issue_id():
    project = Project.objects.create(name="Test Project", code="PRJ")
    status = Status.objects.create(name="Open")
    priority = Priority.objects.create(level="Low")
    user = User.objects.create(username="user1", email="u1@test.com")
    task = Task.objects.create(
        title="Task 1",
        project=project,
        status=status,
        priority=priority,
        creator=user,
        issue_id="PRJ-abc",
    )
    task2 = Task.objects.create(
        title="Task 2", project=project, status=status, priority=priority, creator=user
    )
    assert task2.issue_id.startswith("PRJ-")


@pytest.mark.django_db
def test_comment_serializer_create_with_task_issue_id():
    user = User.objects.create(username="user1", email="u1@test.com")
    project = Project.objects.create(name="Test Project", code="PRJ")
    status = Status.objects.create(name="Open")
    priority = Priority.objects.create(level="Low")
    task = Task.objects.create(
        title="Task", project=project, status=status, priority=priority, creator=user
    )
    data = {"task_issue_id": task.issue_id, "text": "Comment"}
    serializer = CommentSerializer(
        data=data, context={"request": type("obj", (), {"user": user})()}
    )
    assert serializer.is_valid(), serializer.errors
    comment = serializer.save()
    assert comment.text == "Comment"
    assert comment.task == task
    assert comment.author == user


@pytest.mark.django_db
def test_comment_serializer_create_without_task_issue_id():
    user = User.objects.create(username="user1", email="u1@test.com")
    project = Project.objects.create(name="Test Project", code="PRJ")
    status = Status.objects.create(name="Open")
    priority = Priority.objects.create(level="Low")
    task = Task.objects.create(
        title="Task", project=project, status=status, priority=priority, creator=user
    )
    data = {"task_id": task.id, "text": "Comment"}
    serializer = CommentSerializer(
        data=data, context={"request": type("obj", (), {"user": user})()}
    )
    assert serializer.is_valid(), serializer.errors
    comment = serializer.save()
    assert comment.text == "Comment"
    assert comment.task == task
    assert comment.author == user


@pytest.mark.django_db
def test_comment_serializer_create_without_request():
    user = User.objects.create(username="user1", email="u1@test.com")
    project = Project.objects.create(name="Test Project", code="PRJ")
    status = Status.objects.create(name="Open")
    priority = Priority.objects.create(level="Low")
    task = Task.objects.create(
        title="Task", project=project, status=status, priority=priority, creator=user
    )
    data = {"task_id": task.id, "text": "Comment"}
    serializer = CommentSerializer(data=data, context={})
    assert serializer.is_valid(), serializer.errors
    with pytest.raises(IntegrityError):
        serializer.save()


@pytest.mark.django_db
def test_comment_serializer_create_request_without_user():
    user = User.objects.create(username="user1", email="u1@test.com")
    project = Project.objects.create(name="Test Project", code="PRJ")
    status = Status.objects.create(name="Open")
    priority = Priority.objects.create(level="Low")
    task = Task.objects.create(
        title="Task", project=project, status=status, priority=priority, creator=user
    )
    data = {"task_id": task.id, "text": "Comment"}
    serializer = CommentSerializer(data=data, context={"request": object()})
    assert serializer.is_valid(), serializer.errors
    with pytest.raises(IntegrityError):
        serializer.save()
