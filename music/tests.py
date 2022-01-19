from django.contrib.auth.models import User
from django.test import TestCase, Client

from os.path import abspath, join, dirname
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from music.forms import UploadMusicForm


class MetaSetUp(TestCase):
    fixtures = ["test_db.json"]

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(username="test_user")
        self.client.force_login(user=self.user)


class MusicView(MetaSetUp):
    def setUp(self):
        super().setUp()
        self.response = self.client.get(
            reverse('profile-music-page',
                    kwargs={'custom_url': self.user.username})
        )

    def test_open_page(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, 'music/music_list.html')


class MusicUpload(MetaSetUp):
    def setUp(self):
        super().setUp()
        self.response = self.client.get(reverse('music-upload'))

    def test_open_page(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, 'music/music_upload.html')

    def test_upload(self):
        music_path = join(abspath(dirname(__file__)), 'fixtures/test.mp3')
        music_dict = {
            'artist': 'lovecraft',
            'title': 'witchhouse',
        }
        upload_file = open(music_path, 'rb')
        audio_dict = {
            'audio_file': SimpleUploadedFile(upload_file.name,
                                             upload_file.read())
        }
        form = UploadMusicForm(music_dict, audio_dict)
        self.assertTrue(form.is_valid())
        response = self.client.post(reverse('music-upload'), {
            **music_dict,
            **audio_dict
        })
        self.assertEqual(302, response.status_code)
        self.assertTrue(self.user.profile.get_music_list())


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
        response = self.client.post(
            reverse('profile-music-add', kwargs={'music_id': 404})
        )
        self.assertEqual(response.status_code, 404)
        response = self.client.post(
            reverse('profile-music-add', kwargs={'music_id': m.id})
        )
        self.assertContains(response, 'Success', status_code=200)

    def test_add_friends_music(self):
        m = self.user.profile.playlist.all()[0]
        self.assertNotIn(m, self.u2.profile.playlist.all())
        response = self.c2.post(
            reverse('profile-music-add', kwargs={'music_id': m.id})
        )
        self.assertContains(response, 'Success', status_code=200)
        self.assertIn(m, self.u2.profile.playlist.all())


class MusicSearchTest(MusicUpload):

    def setUp(self):
        super(MusicSearchTest, self).setUp()

    def test_search(self):
        self.test_upload()
        response = self.client.post(
            reverse('profile-music-page', kwargs={'custom_url': self.user.profile.custom_url}),
            {'query': 'lovecraft'}
        )
        self.assertEqual(200, response.status_code)

    def test_add_music_from_search(self):
        self.test_upload()
        response = self.client.post(
            reverse('profile-music-add-from-search', kwargs={'music_id': 1})
        )
        self.assertEqual(200, response.status_code)
        self.assertTrue(self.user.profile.playlist.all())


class MusicRemoval(MusicUpload):

    def setUp(self):
        super().setUp()

    def test_music_removal_from_users_playlist(self):
        self.test_upload()
        self.client.post(
            reverse('profile-music-add-from-search', kwargs={'music_id': 1})
        )
        self.assertTrue(self.user.profile.playlist.all())
        response = self.client.post(
            reverse('music-remove', kwargs={'music_id': 1})
        )
        self.assertEqual(302, response.status_code)
