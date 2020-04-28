"""
Consumers module
"""


import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.contrib.auth.models import User

from .models import Message, Chat


class ChatConsumer(WebsocketConsumer):

    """
    ChatConsumer class
    """

    def fetch_messages(self, room_name: str) -> None:
        """
        Fetching messages during connection to a server
        :param room_name: room_id
        :return: None
        """
        chat = Chat.objects.get(id=int(room_name))
        messages = chat.messages.all()
        content = {
            'messages': self.messages_to_json(messages)
        }
        self.send(text_data=json.dumps(content))

    def messages_to_json(self, messages: list) -> list:
        """
        Converting all messages to json
        :param messages: messaegs
        :return: list
        """
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    def message_to_json(self, message: Message) -> dict:
        """
        Convert message data to json
        :param message: message
        :return: dict
        """
        return {
            'author': message.author.username,
            'message': message.message,
            'date': str(message.date)
        }

    def connect(self) -> None:
        """
        connecting to a server
        :return: None
        """
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()
        self.fetch_messages(self.room_name)

    def disconnect(self, close_code) -> None:
        """
        Disconnect
        :param close_code: code
        :return: None
        """
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data) -> None:
        """
        Receive messages and write message to db
        :param text_data: json
        :return: None
        """
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        if not message.isspace():
            author_user = User.objects.get(id=int(text_data_json['author']))
            new_message = Message.objects.create(
                author=author_user,
                message=text_data_json['message'])

            chat = Chat.objects.get(id=int(text_data_json['chat_id']))
            chat.messages.add(new_message)
            chat.save()

            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': self.message_to_json(new_message)
                }
            )

    def chat_message(self, event: dict) -> None:
        """
        Send a message to a socket
        :param event: dict
        :return: None
        """
        message = event['message']

        async_to_sync(self.send(text_data=json.dumps({
            'messages': message,
        })))
