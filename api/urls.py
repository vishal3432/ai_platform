from django.urls import path
from .views import TaskListCreateView, TaskDetailView, FileUploadView, SummarizeTextView

urlpatterns = [
    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('tasks/<int:task_id>/upload/', FileUploadView.as_view(), name='file-upload'),
    path('summarize-text/', SummarizeTextView.as_view(), name='summarize-text'),
]
