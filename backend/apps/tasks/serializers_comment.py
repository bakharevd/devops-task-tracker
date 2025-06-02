from rest_framework import serializers

from .models import Comment, Task
from ..users.serializers import UserSerializer


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    task = serializers.PrimaryKeyRelatedField(read_only=True)
    task_id = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all(),
        write_only=True,
        source='task'
    )
    attachment = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = Comment
        fields = ['id', 'task', 'task_id', 'author', 'text', 'attachment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at', 'task']

    def create(self, validated_data):
        request = self.context.get('request', None)
        if request and hasattr(request, 'user'):
            validated_data['author'] = request.user
        return super().create(validated_data)
