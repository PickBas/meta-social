"""
Modules module
"""

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django_countries.fields import CountryField
from django.template.defaultfilters import slugify
from allauth.account.signals import user_signed_up
from allauth.socialaccount.models import SocialAccount
from django.core.files import File
from urllib.request import urlopen
from tempfile import NamedTemporaryFile
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys


class Community(models.Model):
    """
    Community class
    """
    users = models.ManyToManyField(to=User, related_name='users')
    owner = models.OneToOneField(to=User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True)
    info = models.CharField(max_length=1000, null=True)

    base_image = models.ImageField(upload_to='avatars/communities', default='avatars/users/0.png')
    image = models.ImageField(upload_to='avatars/communities', default='avatars/users/0.png')

    country = CountryField(null=True)

    def posts(self):
        """
        Get community's posts
        """
        return Post.objects.filter(community=self)

    def amount_of_posts(self) -> int:
        """
        Get amount of posts
        :return: int
        """
        return len(self.posts())


class Profile(models.Model):
    """
    User profile class
    """
    GENDER_CHOICES = (
        ('M', 'Мужчина'),
        ('F', 'Женщина'),
        (None, 'Не указано')
    )

    user = models.OneToOneField(to=User, on_delete=models.CASCADE)

    base_image = models.ImageField(upload_to='avatars/users', default='avatars/users/0.png')
    image = models.ImageField(upload_to='avatars/users', default='avatars/users/0.png')

    job = models.CharField(null=True, max_length=100)
    study = models.CharField(null=True, max_length=100)
    biography = models.CharField(max_length=500, null=True)

    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True)
    country = CountryField()
    birth = models.DateField(null=True)
    show_email = models.BooleanField(default=False)

    last_logout = models.DateTimeField(
        default=timezone.now, auto_now=False, auto_now_add=False)
    last_act = models.DateTimeField(
        default=timezone.now, auto_now=False, auto_now_add=False)

    blacklist = models.ManyToManyField(User, 'blacklist')

    communities = models.ManyToManyField(Community)

    def get_name(self):
        if self.user.first_name:
            if self.user.last_name:
                return '{} {}'.format(self.user.first_name, self.user.last_name)
            return self.user.first_name
        return self.user.username

    def check_online_with_last_log(self) -> bool:
        """
        Checking online status using last login/logout
        :param self: User
        :return: bool
        """
        if self.user.last_login is None or self.last_logout is None:
            return False

        if self.user.last_login.hour >= self.last_logout.hour and \
                self.user.last_login.minute >= self.last_logout.minute and \
                self.user.last_login.second >= self.last_logout.second:
            return True
        if self.user.last_login.hour >= self.last_logout.hour and \
                self.user.last_login.minute > self.last_logout.minute:
            return True
        if self.user.last_login.hour > self.last_logout.hour:
            return True

        return False

    def check_online_with_afk(self) -> bool:
        """
        Checking user afk. If user is, online status is changed to offline
        :return: bool
        """
        if self.check_online_with_last_log():
            if timezone.now().hour - self.last_act.hour == 0 and \
                    timezone.now().minute - self.last_act.minute >= 5:
                return False
            if timezone.now().hour - self.last_act.hour >= 1:
                return False
            return True
        return False

    def get_status(self):
        if self.check_online_with_afk():
            return 'Онлайн'
        return 'Оффлайн'

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

    def posts(self):
        """
        Getting user's posts
        """
        return reversed(Post.objects.filter(user=self.user))

    def amount_of_posts(self) -> int:
        """
        Get amount of posts
        :return: int
        """
        return len(self.posts())

    def friends(self):
        friends = [i.to_user for i in list(
            Friend.objects.filter(from_user=self.user))]
        friends += [i.from_user for i in list(
            Friend.objects.filter(to_user=self.user))]

        return friends

    def friendship_inbox_requests(self):
        return FriendshipRequest.objects.filter(to_user=self.user)

    def friendship_requests_count(self):
        return len(self.friendship_inbox_requests())

    def friendship_outbox_requests(self):
        return FriendshipRequest.objects.filter(from_user=self.user)

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
        for friend in self.friends():
            posts += list(friend.profile.posts())
        for community in self.communities.all():
            posts += community.posts()
        posts = sorted(posts, key=lambda x: x.date, reverse=True)
        return posts

    def get_unread_messages_count(self):
        """
        Get amount unread messages
        Сообщения ещё не сделаны тч возвращает 0
        """
        return 0

    def get_music_list(self):
        return Music.objects.filter(user=self.user)

    def get_incoming_messages(self):
        return Messages.objects.filter(to_user=self.user)

    def get_outcoming_messages(self):
        return Messages.objects.filter(from_user=self.user)


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
    creating user profile
    """

    profile = Profile(user=kwargs['user'])
    provider = 'vk' if kwargs['user'].socialaccount_set.filter(
        provider='vk').exists() else 'facebook'

    data = SocialAccount.objects.filter(user=kwargs['user'], provider=provider)

    if data:
        picture = data[0].get_avatar_url()

        if picture:
            save_image_from_url(profile, picture)

    profile.save()


class Post(models.Model):
    """
    Post class
    """
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True)
    community = models.ForeignKey(to=Community, on_delete=models.CASCADE, null=True)
    text = models.TextField()
    date = models.DateTimeField(auto_now=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Посты'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text

    def get_owner(self):
        return self.community if self.community else self.user.profile

    def get_owner_name(self):
        if self.community:
            return self.community.name
        return self.user.username

    def get_link(self):
        if self.community:
            return '/community/' + str(self.community.id) + '/'
        return '/accounts/profile/' + str(self.user.id) + '/'

    def get_images(self):
        return PostImages.objects.filter(post=self)

    def get_images_count(self):
        return PostImages.objects.filter(post=self).count()

    def comments(self):
        return Comment.objects.filter(post=self)

    def amount_of_comments(self):
        return len(self.comments())


class PostImages(models.Model):
    """
    Posts Images class
    """
    post = models.ForeignKey(Post, models.CASCADE)
    image = models.ImageField(upload_to='post/images/')

    def save(self):
        img = Image.open(self.image)
        output = BytesIO()

        new_size = (1280, (img.size[1] * 1280) // img.size[0])

        img = img.resize(new_size, Image.ANTIALIAS)

        img.save(output, format='JPEG', quality=100)
        output.seek(0)

        self.image = InMemoryUploadedFile(output, 'ImageField', "{}.jpg".format(self.image.name.split('.')[0]), 'image/jpeg', sys.getsizeof(output), None)

        super(PostImages, self).save()


class Friend(models.Model):
    """
    Friend class
    """
    from_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='1+')
    to_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='2+')


class FriendshipRequest(models.Model):
    """
    FriendshipRequest class
    """
    from_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='3+')
    to_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='4+')


class Comment(models.Model):
    date = models.DateTimeField(auto_now=True, verbose_name='Дата')
    text = models.CharField(max_length=500, verbose_name='Текст')

    post = models.ForeignKey(to=Post, on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарий'


class Music(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)

    audio_file = models.FileField(upload_to='music')

    artist = models.CharField(default='Автор', max_length=100, verbose_name='Автор')
    title = models.CharField(default='Название', max_length=100, verbose_name='Название')

    class Meta:
        verbose_name = 'Музыка'
        verbose_name_plural = 'Музыка'


class Messages(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="5+", null=True)
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="6+", null=True)
    message = models.CharField(max_length=250, null=True)
    date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Сообщения'
        verbose_name_plural = 'Сообщения'
