"""
Post test.py module
"""
from django.contrib.auth.models import User
from django.test import TestCase, Client
from post.forms import PostForm
from post.models import Post, Comment


class MetaSetUp(TestCase):
    """
    MetaSetUp class
    """
    fixtures = ["test_db.json"]

    def setUp(self):
        """
        Setup
        """
        self.client = Client()
        self.user = User.objects.get(username="test_user")
        self.client.force_login(user=self.user)


class PostView(MetaSetUp):
    """
    PostView Test
    """
    def setUp(self):
        """
        setUp
        """
        super().setUp()
        self.response = self.client.get('/post/1/')

    def test_page(self):
        """
        test_page
        """
        self.assertEqual(self.response.status_code, 200)

    def test_like(self):
        """
        Like test
        """
        self.client.post('/like/1/')
        post = Post.objects.get(id=1)
        # like
        self.assertTrue(post.likes.filter(user=self.user))
        # unlike
        self.client.post('/like/1/')
        self.assertFalse(post.likes.filter(user=self.user))

    def test_comment(self):
        """
        test_comment
        """
        txt = 'Say My Name'
        self.client.post('/post/1/send_comment/', {'text': txt})
        cmnt = Comment.objects.get(user=self.user, text=txt)
        self.assertTrue(cmnt)

        resp = self.client.get('/post/1/get_comments/{}/'.format(404))
        self.assertEqual(resp.status_code, 404)
        resp = self.client.post('/post/1/get_comments/{}/'.format(1))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'post/comments.html')


class PostCreate(MetaSetUp):
    """
    PostCreate class
    """
    def setUp(self):
        """
        SetUp
        """
        super().setUp()

    def test_postform(self):
        """
        create and delete simple text Post
        """
        form_data = {'text': "something wrong?"}
        formset_data = {
            'form-TOTAL_FORMS': '0',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1',
        }
        form = PostForm(data=form_data)
        self.assertTrue(form.is_valid())
        resp = self.client.post('/post/create/', {**form_data, **formset_data})
        self.assertEqual(resp.status_code, 302)
        p = Post.objects.get(user=self.user, text=form_data['text'])
        response = self.client.get('/post/{}/'.format(p.id))
        self.assertEqual(response.status_code, 200)
        self.client.post('/post/{}/remove/'.format(p.id))
        self.assertFalse(
            Post.objects.filter(user=self.user, text=form_data['text']))


class PostEdit(MetaSetUp):
    """
    PostEdit class
    """
    def setUp(self):
        """
        SetUp
        """
        super().setUp()

    def test_editpost_simple(self):
        """
        test_editpost_simple
        """
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
        response = self.client.get('/post/{}/'.format(p.id))
        self.assertEqual(response.status_code, 200)


class PostLikes(MetaSetUp):
    """
    PostLikes class
    """
    def setUp(self):
        """
        SetUp
        """
        super().setUp()

    def test_like_page(self):
        """
        test_like_page
        """
        self.client.post('/like/1/')
        response = self.client.get('/like_marks/')
        # т.к. там все посты вынимаются из user.profile то проверить
        # то и нечего подтверждение виду
        self.assertTemplateUsed(response, 'profile/like_marks.html')


class PostRetwit(TestCase):
    fixtures = ["test_friends_music_db.json"]

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(username="test_user")
        self.client.force_login(user=self.user)

        self.c2 = Client()
        self.u2 = User.objects.get(username="test_user2")
        self.c2.force_login(user=self.u2)

    def test_retwit_userpost(self):
        form_data = {'text': "something bad?"}
        formset_data = {
            'form-TOTAL_FORMS': '0',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1',
        }
        resp = self.client.post('/post/create/', {**form_data, **formset_data})
        p = Post.objects.get(user=self.user, text=form_data['text'])
        self.assertNotIn(p, self.u2.profile.posts.all())
        resp = self.c2.post('/post/{}/rt/'.format(p.id))
        self.assertEqual(resp.status_code, 302)

        p3 = Post.objects.get(owner=self.user, user=self.u2)
        self.assertIn(p3, self.u2.profile.posts.all())
        self.assertIn(self.u2, p.rt.all())
