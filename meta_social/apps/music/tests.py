from django.contrib.auth.models import User
from django.test import TestCase, Client


class MetaSetUp(TestCase):
    fixtures = ["test_db.json"]

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(username="test_user")
        self.client.force_login(user=self.user)


class MusicView(MetaSetUp):
    def setUp(self):
        super().setUp()
        self.response = self.client.get('/music/{}/'.format(self.user.id))

    def test_open_page(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, 'music/music_list.html')

    # TODO: Изменение порядка


class MusicUpload(MetaSetUp):
    def setUp(self):
        super().setUp()
        self.response = self.client.get('/music/upload/')

    def test_open_page(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, 'music/music_upload.html')

    # TODO: Добавление музыки
