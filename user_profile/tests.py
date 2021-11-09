import os

from PIL import Image
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from core.settings import BASE_DIR
from user_profile.forms import UserUpdateForm, ProfileUpdateForm


class MetaSetUp(TestCase):
    fixtures = ["test_db.json"]

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(username="test_user")
        self.client.force_login(user=self.user)


class ProfileViewTest(MetaSetUp):
    def setUp(self):
        super().setUp()
        self.response = self.client.get('/accounts/profile/{}/'.format(
            self.user.username))

    def test_page(self):
        self.assertEqual(self.response.status_code, 200)

    def test_nonexistent_page(self):
        response = self.client.get('/accounts/profile/non_existent/')
        self.assertEqual(response.status_code, 404)


class ProfileEditTest(MetaSetUp):
    def setUp(self):
        super().setUp()
        self.url = '/accounts/profile/{}/edit/'.format(self.user.username)
        self.response = self.client.get(self.url)

    def test_get_page(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, 'profile/edit_profile.html')
        self.assertEqual(self.response.context['profile'], self.user.profile)

    def test_forms(self):
        f_user_update_data = {'first_name': 'test', 'last_name': 'usertest'}
        upus = UserUpdateForm(f_user_update_data, instance=self.user)
        self.assertTrue(upus.is_valid())
        f_profile_data = {
            'job': 'Есть',
            'study': 'Всю жизнь',
            'biography': 'Трудно найти, легко потерять, тяжело прокормить',
            'gender': 'M',
            'custom_url': self.user.profile.custom_url,
        }
        prfl = ProfileUpdateForm(f_profile_data, instance=self.user.profile)
        self.assertTrue(prfl.is_valid())

    def test_edit_profile(self):
        f_user_update_data = {'first_name': 'test', 'last_name': 'usertest'}
        f_profile_data = {
            'job': 'Есть',
            'study': 'Всю жизнь',
            'biography': 'Трудно найти, легко потерять, тяжело прокормить',
            'gender': 'M',  # LGBTQ+ ???
            'custom_url': self.user.profile.custom_url,
        }
        resp = self.client.post(self.url, {
            **f_user_update_data,
            **f_profile_data,
        })
        self.assertEqual(resp.status_code, 302)
        upuser = User.objects.get(id=self.user.id)
        self.assertEqual(upuser.profile.job, f_profile_data['job'])
        self.assertEqual(upuser.last_name, f_user_update_data['last_name'])

    def test_online(self):
        url = '/ajax/set_online/'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

        resp = self.client.post(url)
        # такое ощущение что это не
        # данные, а ссылка
        # TODO: Здесь нужен нормальный тест
        self.assertContains(resp, 'Success', status_code=200)


class AvatarManagingTest(MetaSetUp):
    def setUp(self):
        super().setUp()
        self.response = self.client.get(reverse('profile-change-avatar'))

    def test_get_page(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, 'profile/change_avatar.html')

    def test_avatar_update(self):
        x_position = 0
        y_position = 0
        width = 1915
        height = 1915
        photo = Image.open(os.path.join(BASE_DIR, 'static/img/unknown_profile.jpg'))
        to_send_image = {
            'base_image': photo,
        }
        to_send_cropper = {
            'x': x_position,
            'y': y_position,
            'width': width,
            'height': height,
        }
        response = self.client.post(reverse('profile-change-avatar'), {
            **to_send_image,
            **to_send_cropper,

        })
        self.assertEqual(response.status_code, 302)


class FriendRequestTest(MetaSetUp):

    def setUp(self):
        super().setUp()

    def test_send_friend_request(self):
        response = self.client.post(
            reverse('friend-request-send', kwargs={'user_id': 2})
        )
        self.assertEqual(response.status_code, 302)


class FilePageTest(MetaSetUp):

    def setUp(self):
        super().setUp()

    def test_get_request(self):
        response = self.client.get(
            reverse('profile-files-page', kwargs={'user_url': 'test_user'})
        )
        self.assertEqual(response.status_code, 200)
