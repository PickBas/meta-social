from django.contrib.auth.models import User
from django.test import TestCase, Client
from chat.models import Chat


class MetaSetUp(TestCase):
    fixtures = ["test_friends_music_db.json"]

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(username="test_user")
        self.client.force_login(user=self.user)


class ChatView(MetaSetUp):
    def setUp(self):
        super().setUp()
        self.response = self.client.get('/chats/')

    def test_page(self):
        self.assertEqual(self.response.status_code, 200)


# class ChatMeesages(MetaSetUp):
#     def setUp(self):
#         super().setUp()
#         self.response = self.client.get('/chat/go_to_chat/1/')

#     def test_page(self):
#         self.assertEqual(self.response.status_code, 200)
#         self.assertTemplateUsed(self.response, 'chat/message.html')

#     def test_send_text_message(self):
#         self.assertTrue(True)


class RoomConversationTest(TestCase):
    fixtures = ["test_friends_music_db.json"]

    def setUp(self):
        self.client = Client()
        self.u = User.objects.get(username="test_user")
        self.client.force_login(user=self.u)

        self.c2 = Client()
        self.u2 = User.objects.get(username="test_user2")
        self.c2.force_login(user=self.u2)

        self.c3 = Client()
        self.u3 = User.objects.get(username="test_user3")
        self.c3.force_login(user=self.u3)

    def test_chat_move(self):
        move_url = '/chats/{}/{}/'.format(self.u.id, self.u2.id)
        resp = self.client.post(move_url)
        self.assertEqual(resp.status_code, 302)
        name = self.u.username + ' ' + self.u2.username
        chats = Chat.objects.get(chat_name=name)
        self.assertTrue(chats)

    def test_flow(self):
        data_create = {'text': 'simple chat'}
        resp = self.client.post('/chat/create/', data_create)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'chat/chatlist.html')

        cur_cht = self.u.profile.chats.get(chat_name=data_create['text'])
        self.assertTrue(cur_cht)

        self.assertNotIn(self.u2, cur_cht.participants.all())
        self.assertNotIn(self.u3, cur_cht.participants.all())

        add_url2 = '/chat/{}/add/{}/'.format(cur_cht.id,
                                             self.u2.id)  # add_to_chat
        resp = self.client.get(add_url2)
        self.assertEqual(resp.status_code, 404)
        resp = self.client.post(add_url2)
        self.assertEqual(resp.status_code, 302)

        add_url3 = '/chat/{}/add/{}/'.format(cur_cht.id,
                                             self.u3.id)  # add_to_chat
        resp = self.client.post(add_url3)
        self.assertEqual(resp.status_code, 302)

        self.assertIn(self.u2, cur_cht.participants.all())
        self.assertIn(self.u3, cur_cht.participants.all())

        # make_admin
        self.assertNotIn(self.u2, cur_cht.administrators.all())
        url_adm = '/chat/{}/makeadmin/{}/'.format(cur_cht.id, self.u2.id)
        resp = self.client.get(url_adm)
        self.assertEqual(resp.status_code, 404)
        resp = self.client.post(url_adm)
        self.assertEqual(resp.status_code, 302)
        self.assertIn(self.u2, cur_cht.administrators.all())

        # edit_chat_name
        edit_url = '/chat/edit_chat_name/{}/'.format(cur_cht.id)
        resp = self.c2.get(edit_url)
        self.assertEqual(resp.status_code, 404)
        new_data = {'text': 'new name'}
        resp = self.c2.post(edit_url, new_data)
        self.assertEqual(resp.status_code, 302)
        cur_cht = Chat.objects.get(id=cur_cht.id)
        self.assertEqual(cur_cht.chat_name, new_data['text'])

        # rm_admin
        rmadmin_url = '/chat/{}/rmadmin/{}/'.format(cur_cht.id, self.u2.id)
        resp = self.client.get(rmadmin_url)
        self.assertEqual(resp.status_code, 404)
        resp = self.client.post(rmadmin_url)
        self.assertNotIn(self.u2, cur_cht.administrators.all())

    def test_remove_andquit(self):
        data_create = {'text': 'rm your friend'}
        resp = self.client.post('/chat/create/', data_create)
        cur_cht = self.u.profile.chats.get(chat_name=data_create['text'])
        add_url2 = '/chat/{}/add/{}/'.format(cur_cht.id,
                                             self.u2.id)  # add_to_chat
        resp = self.client.post(add_url2)
        add_url3 = '/chat/{}/add/{}/'.format(cur_cht.id,
                                             self.u3.id)  # add_to_chat
        resp = self.client.post(add_url3)

        self.assertIn(self.u2, cur_cht.participants.all())
        self.assertIn(self.u3, cur_cht.participants.all())

        u_remove_u2 = '/chat/{}/remove/{}/'.format(cur_cht.id, self.u2.id)

        resp = self.client.get(u_remove_u2)
        self.assertEqual(resp.status_code, 404)
        resp = self.client.post(u_remove_u2)
        self.assertEqual(resp.status_code, 302)
        self.assertNotIn(self.u2, cur_cht.participants.all())

        quit_url = '/chat/quit/{}/'.format(cur_cht.id)
        resp = self.c3.get(quit_url)
        self.assertEqual(resp.status_code, 404)
        resp = self.c3.post(quit_url)
        self.assertEqual(resp.status_code, 302)
        self.assertNotIn(self.u3, cur_cht.participants.all())

        remove_url = '/chat/{}/remove/'.format(cur_cht.id)  # remove_chat
        resp = self.client.get(remove_url)
        self.assertEqual(resp.status_code, 404)
        resp = self.client.post(remove_url)
        self.assertFalse(
            self.u.profile.chats.filter(chat_name=data_create['text']))


# remove_url = 'chat/{}/remove/'.format(cur_cht.id)  # remove_chat
# quit_url = 'chat/quit/{}/'.format(cur_cht.id)  # quit_room
# path('chat/<int:room_id>/remove/<int:participant_id>/',
# (Conversations.remove_from_chat)),
