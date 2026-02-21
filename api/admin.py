from django.contrib import admin
from .models import Task, File

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'owner', 'created_at']
    list_filter = ['status']

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ['task', 'uploaded_at', 'is_processed']
