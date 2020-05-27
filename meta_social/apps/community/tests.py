from django.contrib.auth.models import User
from django.test import TestCase, Client
from community.forms import CommunityCreateForm, EditCommunityForm
from community.models import Community
from post.models import Post


class MetaSetUp(TestCase):
    fixtures = ["test_friends_music_db.json"]

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(username="test_user")
        self.client.force_login(user=self.user)

        self.c3 = Client()
        self.u3 = User.objects.get(username="test_user3")
        self.c3.force_login(user=self.u3)


class CommunityTest(MetaSetUp):
    def setUp(self):
        super().setUp()

    def test_flow(self):
        url_create = '/community/user/create/'
        resp = self.client.get(url_create)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'community/community_create.html')

        com_data = {
            'name': 'Church',
            'info': 'holy',
            'country': 'RU',
        }
        form = CommunityCreateForm(com_data)
        self.assertTrue(form.is_valid())

        resp = self.client.post(url_create, com_data)
        self.assertEqual(resp.status_code, 302)

        com1 = Community.objects.get(owner=self.user, name=com_data['name'])

        url_com1 = '/community/{}/'.format(com1.custom_url)
        resp = self.client.get(url_com1)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'community/community_page.html')

        form_data = {'text': "Purge the Heretics!"}
        formset_data = {
            'form-TOTAL_FORMS': '0',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1',
        }
        resp = self.client.post('/post/create/{}/'.format(com1.custom_url), {
            **form_data,
            **formset_data
        })
        self.assertEqual(resp.status_code, 302)
        p = Post.objects.get(text=form_data['text'])
        response = self.client.get('/post/{}/'.format(p.id))
        self.assertEqual(response.status_code, 200)

        resp = self.client.get(url_com1 + 'edit/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'community/edit_community.html')

        com_data = {
            'name': 'Church2',
            'info': 'holy',
            'country': 'RU',
            'custom_url': 'Church'
        }
        form = EditCommunityForm(com_data, instance=com1)
        self.assertTrue(form.is_valid())

        resp = self.client.post(url_com1 + 'edit/', com_data)
        self.assertEqual(resp.status_code, 302)
        com1 = Community.objects.get(owner=self.user, name=com_data['name'])
        url_com1 = '/community/{}/'.format(com1.custom_url)

        self.assertNotIn(self.u3, com1.users.all())
        resp = self.c3.post(url_com1 + 'join/')
        self.assertEqual(resp.status_code, 302)
        self.assertIn(self.u3, com1.users.all())

        resp = self.c3.post(url_com1 + 'leave/')
        self.assertEqual(resp.status_code, 302)
        self.assertNotIn(self.u3, com1.users.all())

        # TODO: Удаление админа или овнера не реализовано


class CommiunityList(MetaSetUp):
    def setUp(self):
        super().setUp()

    def test_acess_list(self):
        resp = self.client.get('/community/user/list/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'community/community_list.html')

        resp = self.client.get('/community/user/mylist/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'community/own_community_list.html')

    def test_search(self):
        url_create = '/community/user/create/'
        resp = self.client.get(url_create)
        com_data = {
            'name': 'W40K',
            'info': '40 000',
            'country': 'RU',
        }
        resp = self.client.post(url_create, com_data)
        com1 = Community.objects.get(owner=self.user, name=com_data['name'])

        resp = self.client.post('/community/user/list/', {'query': 'W40'})
        self.assertIn(com1, resp.context['c_matches'])

    # 'community/<str:community_url>/' +
    # 'community/user/list/' +
    # 'community/user/mylist/' +
    # 'community/user/create/' +
    # 'community/<str:community_url>/join/' +
    # 'community/<str:community_url>/leave/' +
    # 'community/<str:community_url>/change_avatar/'
    # 'community/<str:community_url>/edit/' +
