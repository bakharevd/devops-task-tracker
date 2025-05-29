from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Task, Status, Priority

User = get_user_model()


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
            'status',
            'priority'
        ]
        read_only_fields = ['id', 'created_at', 'creator']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['creator'] = request.user
        return super().create(validated_data)
