from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
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
        self.response = self.client.get('/accounts/profile/2/')

    def test_page(self):
        self.assertEqual(self.response.status_code, 200)


class ProfileEditTest(MetaSetUp):
    def setUp(self):
        super().setUp()
        self.url = '/accounts/profile/{}/edit/'.format(self.user.id)
        self.response = self.client.get(self.url)

    def test_get_page(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, 'profile/edit_profile.html')
        self.assertEqual(self.response.context['profile'], self.user.profile)

    def test_edit_profile(self):
        f_user_update_data = {'first_name': 'test', 'last_name': 'usertest'}
        f_profile_data = {
            'job': 'Есть',
            'study': 'Всю жизнь',
            'biography': 'Трудно найти, легко потерять, тяжело прокормить',
            'gender': 'M',  # LGBTQ+ ???
        }
        resp = self.client.post(self.url, {
            **f_user_update_data,
            **f_profile_data,
        })
        self.assertEqual(resp.status_code, 302)
        upuser = User.objects.get(id=self.user.id)
        self.assertEqual(upuser.profile.job, f_profile_data['job'])
        self.assertEqual(upuser.last_name, f_user_update_data['last_name'])

    def test_forms(self):
        f_user_update_data = {'first_name': 'test', 'last_name': 'usertest'}
        upus = UserUpdateForm(f_user_update_data, instance=self.user)
        self.assertTrue(upus.is_valid())
        f_profile_data = {
            'job': 'Есть',
            'study': 'Всю жизнь',
            'biography': 'Трудно найти, легко потерять, тяжело прокормить',
            'gender': 'M',
        }
        prfl = ProfileUpdateForm(f_profile_data, instance=self.user.profile)
        self.assertTrue(prfl.is_valid())


class AvatarManagingTest(MetaSetUp):
    def setUp(self):
        super().setUp()
        self.response = self.client.get('/accounts/profile/change_avatar/')

    def test_get_page(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, 'profile/change_avatar.html')

    def test_forms(self):
        self.assertTrue(True)
