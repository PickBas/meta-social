from django.contrib.auth.models import User
from django.test import TestCase, Client
from post.forms import PostForm
from post.models import Post


class MetaSetUp(TestCase):
    fixtures = ["test_db.json"]

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(username="test_user")
        self.client.force_login(user=self.user)


class PostView(MetaSetUp):
    def setUp(self):
        super().setUp()
        self.response = self.client.get('/post/1/')

    def test_page(self):
        self.assertEqual(self.response.status_code, 200)


class PostCreate(MetaSetUp):
    def setUp(self):
        super().setUp()

    def test_postform(self):
        form_data = {'text': "something wrong?"}
        formset_data = {
            'form-TOTAL_FORMS': '0',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1',
        }
        form = PostForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.client.post('/post/create/', {**form_data, **formset_data})
        p = Post.objects.get(user=self.user, text=form_data['text'])
        response = self.client.get('/post/{}/'.format(p.id))
        self.assertEqual(response.status_code, 200)
