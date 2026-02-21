from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Task, File
from .serializers import TaskSerializer, FileSerializer
from workers.tasks import process_file_task
from services.ai_service import get_summary


# ── Task Views ──────────────────────────────────────────────────────────────

class TaskListCreateView(generics.ListCreateAPIView):
    """GET /api/tasks  →  list all tasks for the logged-in user.
       POST /api/tasks →  create a new task."""
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PUT/PATCH/DELETE /api/tasks/<id>"""
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)


# ── File Upload View ─────────────────────────────────────────────────────────

class FileUploadView(APIView):
    """POST /api/tasks/<task_id>/upload  →  upload a file and kick off background processing."""
    permission_classes = [IsAuthenticated]

    def post(self, request, task_id):
        try:
            task = Task.objects.get(id=task_id, owner=request.user)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        # Save the file record
        file_instance = File.objects.create(task=task, file=file_obj)

        # Kick off background Celery task (non-blocking)
        process_file_task.delay(file_instance.id)

        return Response(
            FileSerializer(file_instance).data,
            status=status.HTTP_202_ACCEPTED
        )


# ── AI Summarize View ────────────────────────────────────────────────────────

class SummarizeTextView(APIView):
    """POST /api/summarize-text  →  summarize raw text using AI."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        text = request.data.get('text', '').strip()
        if not text:
            return Response({'error': 'No text provided'}, status=status.HTTP_400_BAD_REQUEST)

        summary = get_summary(text)
        return Response({'summary': summary})
