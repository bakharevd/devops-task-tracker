from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Task, Status, Priority, Project

User = get_user_model()


class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class ProjectSerializer(serializers.ModelSerializer):
    members = UserSimpleSerializer(read_only=True, many=True)
    members_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        write_only=True,
        source='members'
    )

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'members', 'members_ids']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        members = validated_data.pop('members', [])
        project = Project.objects.create(**validated_data)
        project.members.set(members)
        return project

    def update(self, instance, validated_data):
        members = validated_data.pop('members', None)
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        if members is not None:
            instance.members.set(members)
        return instance


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['id', 'name']


class PrioritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Priority
        fields = ['id', 'level']


class TaskSerializer(serializers.ModelSerializer):
    creator = serializers.StringRelatedField(read_only=True)
    assignee = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        allow_null=True,
        required=False
    )
    project = ProjectSerializer(read_only=True)
    project_id = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(),
        write_only=True,
        source='project'
    )
    status = serializers.PrimaryKeyRelatedField(
        queryset=Status.objects.all()
    )
    priority = serializers.PrimaryKeyRelatedField(
        queryset=Priority.objects.all()
    )

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'created_at',
            'updated_at',
            'due_date',
            'creator',
            'assignee',
            'project',
            'project_id',
            'status',
            'priority'
        ]
        read_only_fields = ['id', 'created_at', 'creator', 'project']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['creator'] = request.user
        return super().create(validated_data)
