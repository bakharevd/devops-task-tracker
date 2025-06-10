import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from apps.users.models import Position
from apps.users.serializers import (
    UserSerializer,
    UserCreateSerializer,
    PositionSerializer,
)

User = get_user_model()


@pytest.mark.django_db
def test_position_serializer():
    serializer = PositionSerializer(data={"name": "Developer"})
    assert serializer.is_valid()
    position = serializer.save()
    assert position.name == "Developer"
    assert str(position) == "Developer"


@pytest.mark.django_db
def test_user_serializer():
    position = Position.objects.create(name="Developer")
    user = User.objects.create(
        username="testuser",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        position=position,
    )
    serializer = UserSerializer(user)
    data = serializer.data
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert data["first_name"] == "Test"
    assert data["last_name"] == "User"
    assert data["position"]["name"] == "Developer"
    assert "avatar_url" in data


@pytest.mark.django_db
def test_user_serializer_create():
    position = Position.objects.create(name="Developer")
    data = {
        "username": "newuser",
        "email": "new@example.com",
        "first_name": "New",
        "last_name": "User",
        "position_id": position.id,
        "password": "testpass123",
    }
    serializer = UserSerializer(data=data)
    assert serializer.is_valid()
    user = serializer.save()
    assert user.username == "newuser"
    user.refresh_from_db()
    assert user.check_password("testpass123")


@pytest.mark.django_db
def test_user_create_serializer():
    position = Position.objects.create(name="Developer")
    data = {
        "username": "createuser",
        "email": "create@example.com",
        "first_name": "Create",
        "last_name": "User",
        "position_id": position.id,
        "password": "testpass123",
    }
    serializer = UserCreateSerializer(data=data)
    assert serializer.is_valid()
    user = serializer.save()
    assert user.username == "createuser"
    assert user.check_password("testpass123")
