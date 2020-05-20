from django.contrib.auth.models import User
from django.test import TestCase, Client


class MetaSetUp(TestCase):
    fixtures = ["test_db.json"]

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(username="test_user")
        self.client.force_login(user=self.user)


# class FriendsSearchView(MetaSetUp):
#     def setUp(self):
#         super().setUp()
#         self.response = self.client.get('/friends/search/')

#     def test_friend_post(self):
#         response = self.client.post('/friends/search/', {'name': 'test_user2'})
#         self.assertEqual(response.status_code, 200)
#         # self.assertEqual(self.response.status_code, 200)
#         self.assertTrue(
#             User.objects.get(
#                 username="test_user2") in response.context['matches'])


class FriendsListView(MetaSetUp):
    def setUp(self):
        super().setUp()
        self.response = self.client.get('/friends/1/')

    def test_page(self):
        self.assertEqual(self.response.status_code, 200)
