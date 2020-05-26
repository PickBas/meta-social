from django.contrib.auth.models import User
from django.test import TestCase, Client
from friends.models import FriendshipRequest as FR


class MetaSetUp(TestCase):
    fixtures = ["test_friends_music_db.json"]

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(username="test_user")
        self.client.force_login(user=self.user)


class FriendsListView(MetaSetUp):
    def setUp(self):
        super().setUp()
        self.response = self.client.get('/friends/')

    def test_page(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, 'friends/friends_list.html')

        response = self.client.get('/friends/',
                                   {'username': self.user.username)
        self.assertEqual(response.status_code, 200)


class BlacklistTest(MetaSetUp):
    def setUp(self):
        super().setUp()
        self.response = self.client.get('/friends/blacklist/')

    def test_page(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, 'friends/blacklist.html')
        self.assertEqual(self.response.context['friends_pages'], 'blacklist')


class BlacklistAdd(MetaSetUp):
    """
    В тестовой базе у нас 3 пользователя:
    test_user, test_user2, test_user3
    test_user2, test_user3 дружать c test_user
    """
    def setUp(self):
        super().setUp()
        self.blackuser = User.objects.get(username="test_user2")

    def test_addblack(self):
        url = '/friends/add_blacklist/{}/'.format(self.blackuser.id)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        bquery = self.user.profile.blacklist.filter(id=self.blackuser.id)
        self.assertTrue(bquery)
        # TODO: Тут всякие тесты на доступы к юзеру в черном списке
        url = '/friends/add_blacklist/{}/'.format(42)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 404)

    def test_remblack(self):
        url = '/friends/add_blacklist/{}/'.format(self.blackuser.id)
        self.client.post(url)
        bquery = self.user.profile.blacklist.filter(id=self.blackuser.id)
        self.assertTrue(bquery)
        url = '/friends/remove_blacklist/{}/'.format(self.blackuser.id)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)

        url = '/friends/remove_blacklist/{}/'.format(42)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 404)

        url = '/friends/remove_blacklist/{}/'.format(self.blackuser.id)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        bquery = self.user.profile.blacklist.filter(id=self.blackuser.id)
        self.assertFalse(bquery)

    def test_remove_friend(self):
        bquery = self.user.profile.friends.filter(id=self.blackuser.id)
        self.assertTrue(bquery)

        url = '/friends/remove_friend/{}/'.format(self.blackuser.id)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        bquery = self.user.profile.friends.filter(id=self.blackuser.id)
        self.assertFalse(bquery)

        url = '/friends/remove_friend/{}/'.format(self.blackuser.id)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 404)

        url = '/friends/remove_friend/{}/'.format(42)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 404)


class FriendsRequestsTest(MetaSetUp):
    fixtures = ["test_friends_music_db.json"]

    def setUp(self):
        self.c2 = Client()
        self.user2 = User.objects.get(username="test_user2")
        self.c2.force_login(user=self.user2)
        self.c3 = Client()
        self.user3 = User.objects.get(username="test_user3")
        self.c3.force_login(user=self.user3)

    def test_request(self):
        self.assertFalse(
            FR.objects.filter(from_user=self.user2, to_user=self.user3))

        url = '/friends/send_request/{}/'.format(self.user3.id)
        resp = self.c2.post(url)
        self.assertEqual(resp.status_code, 200)
        fr_obj = FR.objects.get(from_user=self.user2, to_user=self.user3)
        self.assertTrue(fr_obj)

        resp = self.c2.get(url)
        self.assertEqual(resp.status_code, 404)

        url = '/friends/requests/'
        resp = self.c2.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['friendship']['outcoming'][0], fr_obj)
        self.assertTemplateUsed(resp, 'friends/requests.html')

        resp = self.c3.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['friendship']['incoming'][0], fr_obj)

        url = '/friends/cancel_request/{}/'.format(self.user3.id)
        resp = self.c2.post(url)
        self.assertNotIn(
            fr_obj, FR.objects.filter(from_user=self.user2))
        url = '/friends/requests/'
        resp = self.c2.get(url)
        self.assertNotIn(fr_obj, resp.context['friendship']['outcoming'])

    def test_acsept(self):
        url = '/friends/send_request/{}/'.format(self.user3.id)
        self.c2.post(url)

        url = '/friends/accept_request/{}/'.format(self.user2.id)
        resp = self.c3.post(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(self.user2,
                      self.user3.profile.friends.all())

        # TODO: Осталась проверка написание доступа к ресурсов не
        # френдов, к доступу ресурсов и написанию сообщений
        # блэклистнутому пользователю
