from django.contrib.auth.models import User
from django.test import TestCase, Client

from os import walk
from os.path import abspath, join, dirname
from shutil import rmtree
from tempfile import mkdtemp
from django.core.files.storage import FileSystemStorage
from django_s3_storage.storage import StaticS3Storage
from django.test.utils import override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
# import mock
from music.models import Music
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

    # @mock.patch('django_s3_storage.storage.StaticS3Storage', FileSystemStorage)
    # @mock.patch.object(StaticS3Storage, '_save', FileSystemStorage()._save)
    def test_upload(self):
        music_path = join(abspath(dirname(__file__)), 'fixtures/test.mp3')
        media_folder = mkdtemp()
        print(music_path)
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

        with override_settings(
                MEDIA_ROOT=media_folder,
                STATIC_ROOT=media_folder,
        ):
            resp = self.client.post('/music/upload/', {
                **music_dict,
                **audio_dict
            })

            for (dirpath, dirnames, filenames) in walk(media_folder):
                print("{} {} {}".format(dirpath, dirnames, filenames))
            self.assertTrue(Music.objects.all())

            self.assertEqual(resp.status_code, 302)
            rmtree(media_folder)  # post test

            # TODO: mock нечего работает


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
