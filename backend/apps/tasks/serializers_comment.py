from rest_framework import serializers

from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    attachment = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = Comment
        fields = ['id', 'task', 'author', 'text', 'attachment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'created_at']

    def create(self, validated_data):
        request = self.context.get('request', None)
        if request and hasattr(request, 'user'):
            validated_data['author'] = request.user
        return super().create(validated_data)
