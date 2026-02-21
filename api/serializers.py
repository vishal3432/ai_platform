from rest_framework import serializers
from .models import Task, File


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['id', 'file', 'summary', 'uploaded_at', 'is_processed']
        read_only_fields = ['summary', 'is_processed']


class TaskSerializer(serializers.ModelSerializer):
    files = FileSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'files', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
