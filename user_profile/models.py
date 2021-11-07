"""
Meta social user profile model
"""

from urllib.request import urlopen
from tempfile import NamedTemporaryFile
import humanize

from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.core.files import File
from django.dispatch import receiver

from django_countries.fields import CountryField
from allauth.account.signals import user_signed_up
from allauth.socialaccount.models import SocialAccount

from community.models import Community
from post.models import Post
from chat.models import Chat
from friends.models import FriendshipRequest
from music.models import Music


class PlayPosition(models.Model):
    """
    Model contains music, order and user

    :param position: ForeignKey to :class:`music.models.Music`
    :param plist: ForeignKey to :class:`user_profile.models.Profile`
    :param order: order of music
    """
    position = models.ForeignKey(to=Music, on_delete=models.CASCADE)
    plist = models.ForeignKey('Profile', on_delete=models.CASCADE)
    order = models.IntegerField(blank=True, null=True)

    def add_order(self):
        """
        Adds order
        """
        self.order = len(self.plist.playlist.all()) + 1


class Profile(models.Model):
    """
    User profile model
    """
    GENDER_CHOICES = (
        ('M', 'Мужчина'),
        ('F', 'Женщина'),
        (None, 'Не указано')
    )

    user = models.OneToOneField(to=User, on_delete=models.CASCADE)

    custom_url = models.CharField(max_length=50,
                                  default='',
                                  unique=True,
                                  help_text='Required. 50 characters or fewer. Letters, digits and @/./+/-/_ only.',
                                  validators=[User.username_validator],
                                  error_messages={
                                      'unique': 'A user with that username already exists.',
                                      'invalid': 'Invalid url'
                                  }, )

    base_image = models.ImageField(upload_to='avatars/users', default='avatars/users/unknown_profile.jpg')
    image = models.ImageField(upload_to='avatars/users', default='avatars/users/unknown_profile.jpg') 

    job = models.CharField(null=True, max_length=100)
    study = models.CharField(null=True, max_length=100)
    biography = models.CharField(max_length=500, null=True)

    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True)
    country = CountryField()
    birth = models.DateField(null=True)
    show_email = models.BooleanField(default=False)

    last_act = models.DateTimeField(
        default=timezone.now,
        auto_now=False,
        auto_now_add=False
    )

    posts = models.ManyToManyField(Post, 'posts')
    blacklist = models.ManyToManyField(User, 'blacklist')
    communities = models.ManyToManyField(Community)
    liked_posts = models.ManyToManyField(Post, 'liked_posts')
    friends = models.ManyToManyField(User, related_name='friendlist')
    chats = models.ManyToManyField(Chat)
    playlist = models.ManyToManyField(Music, related_name='playlist',
                                      through='PlayPosition')

    def unread_chats_count(self):
        """
        Returns the number of unread chats

        :rtype: int
        """
        count = 0
        for chat in self.chats.all():
            messages = chat.get_unread_messages().exclude(author=self.user)
            if len(messages) > 0:
                count += 1

        return count

    def get_name(self):
        """
        Returns the name, surname of the user, if they are not specified then returns the nickname

        :rtype: str
        """
        if self.user.first_name:
            if self.user.last_name:
                return '{} {}'.format(self.user.last_name, self.user.first_name)
            return self.user.first_name
        return self.user.username

    def get_status(self):
        """
        Returns humanized status of user

        :rtype: str
        """
        duration = timezone.now() - self.last_act
        minutes = (duration.total_seconds() % 3600) // 60

        if minutes <= 5:
            return 'Онлайн'

        humanize.i18n.activate('ru_RU')

        return 'Был(а) в сети {} назад'.format(humanize.naturaldelta(duration))

    def get_social_accounts(self) -> list:
        """
        Getting social accounts

        :return: list
        """
        return [i.provider for i in self.user.socialaccount_set.all()]

    def get_social_data(self, provider):
        """
        Getting social data

        :param provider:
        """
        return self.user.socialaccount_set.filter(provider=provider)[0].extra_data

    def friendship_inbox_requests(self):
        """
        Returns incoming friendship request objects

        :rtype: django queryset
        """
        return FriendshipRequest.objects.filter(to_user=self.user)

    def friendship_inbox_users(self):
        """
        Returns incoming friendship user objects

        :rtype: list
        """
        return [i.from_user for i in self.friendship_inbox_requests()]

    def friendship_requests_count(self):
        """
        Returns the number of incoming friendship requests

        :rtype: int
        """
        return len(self.friendship_inbox_requests())

    def friendship_outbox_requests(self):
        """
        Returns outcoming friendship request objects

        :rtype: django queryset
        """
        return FriendshipRequest.objects.filter(from_user=self.user)

    def friendship_outbox_users(self):
        """
        Returns outcoming friendship user objects

        :rtype: list
        """
        return [i.to_user for i in self.friendship_outbox_requests()]

    def amount_of_friends(self) -> int:
        """
        Get amount of friends
        :return: int
        """
        return len(self.friends())

    def get_newsfeed(self) -> list:
        """
        Get user's news feed
        :return: list
        """
        posts = []
        for friend in self.friends.all():
            posts += list(friend.profile.posts.all())
        for community in self.communities.all():
            posts += community.posts.all()
        posts = sorted(posts, key=lambda x: x.date, reverse=True)
        return posts

    def get_music_list(self):
        """
        Returns all music in user playlist
        """
        res = [PlayPosition.objects.get(position=m, plist=self) for m in self.playlist.all()]
        res.sort(key=lambda x: x.order, reverse=True)
        return res

    def add_music(self, music):
        """
        Adds music to playlist

        :param music: music model
        :type music: :class:`user_profile.models.PlayPosition`
        """
        self.playlist.add(music)

    def change_playlist(self, new_order):
        """
        Not ready function for infinity scroll
        """
        ymusics = [PlayPosition.objects.get(position=m, plist=self) for m in self.playlist.all()]
        ymusics.sort(key=lambda x: x.order)
        if len(new_order) < len(ymusics):
            pass  # TODO для постепенной загрузки infinite scroll
        new_mlist = []
        for i in new_order:
            new_mlist.append(ymusics[i - 1])
        new_mlist.reverse()

        for i in range(len(new_order)):
            new_mlist[i].order = i + 1
            new_mlist[i].save()

    def get_recommended_communities(self):
        """
        Method for getting recommended communities

        :return: recommended communities
        :rtype: list
        """
        communities = list(Community.objects.all())
        communities.sort(key=lambda c: c.users.count())
        communities = list(dict.fromkeys(communities))
        return communities[:6]


def save_image_from_url(profile, image_url):
    """
    Saving image from url to profile model
    """
    img_temp = NamedTemporaryFile(delete=True)
    img_temp.write(urlopen(image_url).read())
    img_temp.flush()

    profile.base_image.save('image_{profile.id}', File(img_temp))
    profile.image.save('image_{profile.id}', File(img_temp))


@receiver(user_signed_up)
def create_user_profile(sender, **kwargs) -> None:
    """
    Creating user profile
    """

    profile = Profile(user=kwargs['user'])
    profile.custom_url = profile.user.username
    provider = 'vk' if kwargs['user'].socialaccount_set.filter(
        provider='vk').exists() else 'facebook'

    data = SocialAccount.objects.filter(user=kwargs['user'], provider=provider)

    if data:
        picture = data[0].get_avatar_url()

        if picture:
            save_image_from_url(profile, picture)

    profile.save()
