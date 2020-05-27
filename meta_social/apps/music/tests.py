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
        self.response = self.client.get('/accounts/profile/{}/music/'.format(
            self.user.username))

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


class AddExistedMusic(TestCase):
    fixtures = ["test_friends_music_db.json"]

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(username="test_user")
        self.client.force_login(user=self.user)

        self.c2 = Client()
        self.u2 = User.objects.get(username="test_user2")
        self.c2.force_login(user=self.u2)

    def test_existed_inplist_music(self):
        m = self.user.profile.playlist.all()[0]
        self.assertTrue(m)
        resp = self.client.post('/music/{}/add/'.format(404))
        self.assertEqual(resp.status_code, 404)

        resp = self.client.post('/music/{}/add/'.format(m.id))

        self.assertContains(resp, 'Success', status_code=200)

    def test_add_friend_music(self):
        m = self.user.profile.playlist.all()[0]

        self.assertNotIn(m, self.u2.profile.playlist.all())
        resp = self.c2.post('/music/{}/add/'.format(m.id))

        self.assertContains(resp, 'Success', status_code=200)
        self.assertIn(m, self.u2.profile.playlist.all())
