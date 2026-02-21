import json
from channels.generic.websocket import AsyncWebsocketConsumer


class TaskConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time task status updates.
    Frontend connects to ws://localhost:8000/ws/tasks/<task_id>/
    When a Celery worker finishes processing, it sends a message here.
    """

    async def connect(self):
        self.task_id = self.scope['url_route']['kwargs']['task_id']
        self.group_name = f'task_{self.task_id}'

        # Join the task group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # Called when a message is sent to this group from a Celery worker
    async def task_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'task_update',
            'task_id': self.task_id,
            'message': event['message'],
        }))
