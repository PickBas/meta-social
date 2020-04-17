import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.contrib.auth.models import User

from .models import Message, Chat


class ChatConsumer(WebsocketConsumer):

    def fetch_messages(self, room_name):
        chat = Chat.objects.get(id=int(room_name))
        messages = chat.messages.all()
        content = {
            'messages': self.messages_to_json(messages)
        }
        self.send(text_data=json.dumps(content))

    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    def message_to_json(self, message):
        return {
            'author': message.author.username,
            'message': message.message,
            'date': str(message.date)
        }

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()
        self.fetch_messages(self.room_name)

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        author_user = User.objects.get(id=int(text_data_json['author']))
        new_message = Message.objects.create(
            author=author_user,
            message=text_data_json['message'])

        chat = Chat.objects.get(id=int(text_data_json['chat_id']))
        chat.messages.add(new_message)
        chat.save()

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': self.message_to_json(new_message)
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        async_to_sync(self.send(text_data=json.dumps({
            'messages': message
        })))
