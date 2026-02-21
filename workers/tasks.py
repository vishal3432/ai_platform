"""
workers/tasks.py

Background tasks powered by Celery.
These run separately from the web server so uploads don't block the API.
"""
import os
import django

# Make sure Django settings are loaded when this module runs as a worker
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from celery import shared_task
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from services.ai_service import get_summary


@shared_task
def process_file_task(file_id: int):
    """
    Background task: reads an uploaded file, summarizes it with AI,
    saves the summary, and notifies the frontend via WebSocket.

    Pro Tip: We read the file line-by-line (streaming) so even a 1GB
    CSV won't crash the server by loading everything into RAM.
    """
    # Import here to avoid circular imports
    from api.models import File

    try:
        file_instance = File.objects.get(id=file_id)
        file_path = file_instance.file.path

        # ── Stream-read the file (memory efficient) ────────────────────────
        lines = []
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f):
                lines.append(line.strip())
                if i >= 99:  # Read first 100 lines for summarization
                    break

        content = '\n'.join(lines)

        # ── Generate AI summary ────────────────────────────────────────────
        summary = get_summary(content)

        # ── Save summary to DB ─────────────────────────────────────────────
        file_instance.summary = summary
        file_instance.is_processed = True
        file_instance.save()

        # ── Notify frontend via WebSocket (real-time update!) ──────────────
        channel_layer = get_channel_layer()
        task_group = f'task_{file_instance.task.id}'

        async_to_sync(channel_layer.group_send)(
            task_group,
            {
                'type': 'task_update',
                'message': f'File processed! Summary: {summary[:100]}...',
            }
        )

        return f"File {file_id} processed successfully."

    except Exception as e:
        return f"Error processing file {file_id}: {str(e)}"
