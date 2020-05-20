from django.contrib.auth.models import User
from django.test import TestCase, Client
import json


class MetaSetUp(TestCase):
    fixtures = ["test_db.json"]

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(username="test_user")
        self.client.force_login(user=self.user)


class ChatView(MetaSetUp):
    def setUp(self):
        super().setUp()
        self.response = self.client.get('/chats/1/')

    def test_page(self):
        self.assertEqual(self.response.status_code, 200)


class ChatMeesages(MetaSetUp):
    def setUp(self):
        super().setUp()
        self.response = self.client.get('/chat/go_to_chat/1/')

    def test_page(self):
        self.assertEqual(self.response.status_code, 200)

    # TODO: Исправить
    def test_send_post(self):
        response = self.client.get('/chat/go_to_chat/1/send_mes/')
        self.assertEqual(response.status_code, 404)
        response = self.client.post('/chat/go_to_chat/1/send_mes/',
                                    {'text': 'Wake up!'})
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(result['sender'], 'test_user')
