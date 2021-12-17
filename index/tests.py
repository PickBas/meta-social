from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse


class MetaSetUp(TestCase):
    fixtures = ["test_friends_music_db.json"]

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(username="test_user")
        self.client.force_login(user=self.user)


class IndexViewTest(MetaSetUp):
    def setUp(self):
        super().setUp()
        self.response = self.client.get(reverse("home"))

    def test_login(self):
        self.assertEqual(self.response.status_code, 200)

    def test_unauth_client(self):
        unauth_client = Client()
        response = unauth_client.get(reverse("home"))
        self.assertEqual(response.status_code, 302)
        response = unauth_client.get(reverse("home"), follow=True)
        last_url, status = response.redirect_chain[-1]
        self.assertIn(reverse("account_login"), last_url)

    def test_update_nav(self):
        response = self.client.post(reverse('nav-update'))
        self.assertEqual(200, response.status_code)


class GlobalSearchTest(MetaSetUp):
    def setUp(self):
        super().setUp()

    def test_search(self):
        resp = self.client.post(reverse('global-search'), {
            'query': 'test',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['users']), 2)
        self.assertEqual(len(resp.context['communities']), 0)
        self.assertTemplateUsed(resp, 'search_list.html')
        resp = self.client.post(reverse('global-search'), {
            'query': 'Dreams',
        })
        self.assertEqual(len(resp.context['music']), 3)

    def test_page(self):
        self.response = self.client.get(
            reverse('profile-page', kwargs={'custom_url': 'test_user'})
        )
        self.assertEqual(self.response.status_code, 200)

    def test_get_reqeust(self):
        self.response = self.client.get(reverse('global-search'))
        self.assertEqual(404, self.response.status_code)


class FriendsListView(MetaSetUp):
    def setUp(self):
        super().setUp()
        self.response = self.client.get(reverse('friends-list'))

    def test_page(self):
        self.assertEqual(self.response.status_code, 200)


class ChatView(MetaSetUp):
    def setUp(self):
        super().setUp()
        self.response = self.client.get(reverse('chat-list'))

    def test_page(self):
        self.assertEqual(self.response.status_code, 200)


class PostView(MetaSetUp):
    def setUp(self):
        super().setUp()
        self.response = self.client.get(
            reverse('post-page', kwargs={'post_id': 1})
        )

    def test_page(self):
        self.assertEqual(self.response.status_code, 200)
