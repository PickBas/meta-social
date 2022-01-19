"""
Post test.py module
"""
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from post.forms import PostForm
from post.models import Post, Comment


class MetaSetUp(TestCase):

    fixtures = ["test_db.json"]

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(username="test_user")
        self.client.force_login(user=self.user)


class PostView(MetaSetUp):

    def setUp(self):
        super().setUp()
        self.response = self.client.get(
            reverse('post-page', kwargs={'post_id': 1})
        )

    def test_page(self):
        self.assertEqual(self.response.status_code, 200)

    def test_like(self):
        self.client.post(reverse('post-like', kwargs={'post_id': 1}))
        post = Post.objects.get(id=1)
        # like
        self.assertTrue(post.likes.filter(user=self.user))
        # unlike
        self.client.post(reverse('post-like', kwargs={'post_id': 1}))
        self.assertFalse(post.likes.filter(user=self.user))

    def test_comment(self):
        txt = 'Say My Name'
        self.client.post(
            reverse('post-send-comment', kwargs={'post_id': 1}),
            {'text': txt})
        cmnt = Comment.objects.get(user=self.user, text=txt)
        self.assertTrue(cmnt)
        resp = self.client.get(reverse('post-comments', kwargs={'post_id': 1,
                                                                'is_all': 404}))
        self.assertEqual(resp.status_code, 404)
        resp = self.client.post(reverse('post-comments', kwargs={'post_id': 1,
                                                                 'is_all': 1}))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'post/comments.html')


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
        resp = self.client.post(
            reverse('profile-post-create'),
            {**form_data, **formset_data})
        self.assertEqual(resp.status_code, 302)
        p = Post.objects.get(user=self.user, text=form_data['text'])
        response = self.client.get(
            reverse('post-page', kwargs={'post_id': p.id})
        )
        self.assertEqual(response.status_code, 200)
        self.client.post(reverse('post-remove', kwargs={'post_id': p.id}))
        self.assertFalse(
            Post.objects.filter(user=self.user, text=form_data['text']))


class PostEdit(MetaSetUp):

    def setUp(self):
        super().setUp()

    def test_editpost_simple(self):
        self.assertTrue(True)
        form_data = {'text': "edit post complete"}
        formset_data = {
            'form-TOTAL_FORMS': '0',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1',
        }
        form = PostForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.client.post('/post/{}/edit/'.format(1), {
            **form_data,
            **formset_data
        })
        p = Post.objects.get(user=self.user, text=form_data['text'])
        self.assertEqual(p.id, 1)
        response = self.client.get(
            reverse('post-page', kwargs={'post_id': p.id})
        )
        self.assertEqual(response.status_code, 200)


class PostLikes(MetaSetUp):

    def setUp(self):
        super().setUp()

    def test_like_page(self):
        self.client.post('/like/1/')
        response = self.client.get('/like_marks/')
        self.assertTemplateUsed(response, 'profile/like_marks.html')


class PostRepost(TestCase):
    fixtures = ["test_friends_music_db.json"]

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(username="test_user")
        self.client.force_login(user=self.user)

        self.c2 = Client()
        self.u2 = User.objects.get(username="test_user2")
        self.c2.force_login(user=self.u2)

    def test_repost_user_post(self):
        form_data = {'text': "something bad?"}
        formset_data = {
            'form-TOTAL_FORMS': '0',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1',
        }
        self.client.post(reverse('profile-post-create'), {**form_data, **formset_data})
        p = Post.objects.get(user=self.user, text=form_data['text'])
        self.assertNotIn(p, self.u2.profile.posts.all())
        resp = self.c2.post(reverse('post-repost', kwargs={'post_id': p.id}))
        self.assertEqual(resp.status_code, 302)
        p3 = Post.objects.get(owner=self.user, user=self.u2)
        self.assertIn(p3, self.u2.profile.posts.all())
        self.assertIn(self.u2, p.rt.all())
