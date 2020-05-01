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
import sys, humanize


class Community(models.Model):
    """
    Community class
    """
    users = models.ManyToManyField(to=User, related_name='users')
    admins = models.ManyToManyField(to=User, related_name='admins')
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
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


class Like(models.Model):
    date = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)


class Post(models.Model):
    """
    Post class
    """
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True)
    community = models.ForeignKey(to=Community, on_delete=models.CASCADE, null=True)
    text = models.TextField()
    date = models.DateTimeField(auto_now=True, verbose_name='Дата создания')

    likes = models.ManyToManyField(Like, blank=True, related_name='likes')

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
        return self.user.profile.get_name()

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

    def get_editors(self):
        editors = []
        if self.user:
            editors.append(self.user)
        return editors


class Message(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author_messages", null=True)
    message = models.TextField(null=True)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.author.username


class Chat(models.Model):
    chat_name = models.CharField(max_length=50, null=True)
    participants = models.ManyToManyField(User, related_name="chat_participants")
    messages = models.ManyToManyField(Message, blank=True)
    is_dialog = models.BooleanField(default=False)

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_owner', null=True)
    administrators = models.ManyToManyField(User, related_name='chat_administrators')

    base_image = models.ImageField(upload_to='avatars/users', default='avatars/users/0.png')
    image = models.ImageField(upload_to='avatars/users', default='avatars/users/0.png')

    def last_message(self):
        try:
            return list(self.messages.all().order_by('-date'))[0]
        except:
            return False

    def __str__(self):
        return "{}".format(self.pk)


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

    last_act = models.DateTimeField(
        default=timezone.now, 
        auto_now=False, 
        auto_now_add=False
    )

    blacklist = models.ManyToManyField(User, 'blacklist')
    communities = models.ManyToManyField(Community)
    liked_posts = models.ManyToManyField(Post, 'liked_posts')
    friends = models.ManyToManyField(User, related_name='friendlist')
    chats = models.ManyToManyField(Chat)

    def get_name(self):
        if self.user.first_name:
            if self.user.last_name:
                return '{} {}'.format(self.user.first_name, self.user.last_name)
            return self.user.first_name
        return self.user.username

    def get_status(self):
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

    def friendship_inbox_requests(self):
        return FriendshipRequest.objects.filter(to_user=self.user)

    def friendship_inbox_users(self):
        return [i.from_user for i in self.friendship_inbox_requests()]

    def friendship_requests_count(self):
        return len(self.friendship_inbox_requests())

    def friendship_outbox_requests(self):
        return FriendshipRequest.objects.filter(from_user=self.user)

    def friendship_outbox_users(self):
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


class PostImages(models.Model):
    """
    Posts Images class
    """
    post = models.ForeignKey(Post, models.CASCADE)
    image = models.ImageField(upload_to='post/images/')
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def save(self):
        img = Image.open(self.image)
        output = BytesIO()

        new_size = (1280, (img.size[1] * 1280) // img.size[0])

        img = img.resize(new_size, Image.ANTIALIAS)

        img.save(output, format='JPEG', quality=100)
        output.seek(0)

        self.image = InMemoryUploadedFile(output, 'ImageField', "{}.jpg".format(self.image.name.split('.')[0]),
                                          'image/jpeg', sys.getsizeof(output), None)

        super(PostImages, self).save()


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
