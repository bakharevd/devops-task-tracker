from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Position

User = get_user_model()


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ['id', 'name']


class UserSerializer(serializers.ModelSerializer):
    position = PositionSerializer(read_only=True)
    position_id = serializers.PrimaryKeyRelatedField(
        queryset=Position.objects.all(),
        write_only=True,
        source='position'
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'position', 'position_id', 'is_superuser']
        read_only_fields = ['id', 'is_superuser']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class UserCreateSerializer(serializers.ModelSerializer):
    position_id = serializers.PrimaryKeyRelatedField(
        queryset=Position.objects.all(),
        write_only=True,
        source='position'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'position_id', 'is_superuser']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
