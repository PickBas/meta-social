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
from image_cropping import ImageRatioField, ImageCropField
from allauth.account.signals import user_signed_up
from allauth.socialaccount.models import SocialAccount
from django.core.files import File
from urllib.request import urlopen
from tempfile import NamedTemporaryFile


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

    image = ImageCropField(blank=True, upload_to='avatars/users', default='avatars/users/0.png')
    cropping = ImageRatioField('image', '256x256')

    job = models.CharField(null=True, max_length=100)
    biography = models.CharField(max_length=500, null=True)

    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True)
    country = CountryField()
    birth = models.DateField(null=True)
    show_email = models.BooleanField(default=False)

    last_logout = models.DateTimeField(default=timezone.now, auto_now=False, auto_now_add=False)
    last_act = models.DateTimeField(default=timezone.now, auto_now=False, auto_now_add=False)

    blacklist = models.ManyToManyField(User, 'blacklist')

    def check_online_with_last_log(self) -> bool:
        """
        Checking onlime status using last login/logout
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
        friends = [i.to_user for i in list(Friend.objects.filter(from_user=self.user))]
        friends += [i.from_user for i in list(Friend.objects.filter(to_user=self.user))]

        return friends

    def friendship_inbox_requests(self):
        return FriendshipRequest.objects.filter(to_user=self.user)

    def friendship_outbox_requests(self):
        return FriendshipRequest.objects.filter(from_user=self.user)

    def amount_of_friends(self) -> int:
        """
        Get amount of friends
        :return: int
        """
        return len(self.friends())

    def communities(self):
        """
        Get communities
        """
        return Communities.objects.filter(user=self.user)

    def amount_of_communities(self) -> int:
        """
        Get amount of communities
        :return: int
        """
        return len(self.communities())

    def get_newsfeed(self) -> list:
        """
        Get user's news feed
        :return: list
        """
        posts = []
        for friend in self.friends():
            posts += list(friend.profile.posts())
        for com in self.communities():
            posts += com.posts()
        posts = sorted(posts, key=lambda x: x.date, reverse=True)
        return posts


def save_image_from_url(profile, image_url):
    img_temp = NamedTemporaryFile(delete=True)
    img_temp.write(urlopen(image_url).read())
    img_temp.flush()

    profile.image.save('image_{profile.id}', File(img_temp))


@receiver(user_signed_up)
def create_user_profile(sender, **kwargs) -> None:
    """
    creating user profile
    """

    profile = Profile(user=kwargs['user'])
    provider = 'vk' if kwargs['user'].socialaccount_set.filter(provider='vk').exists() else 'facebook'

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
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    text = models.TextField()
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text

    def get_images(self):
        return PostImages.objects.filter(post=self)


class PostImages(models.Model):
    """
    Posts Images class
    """
    post = models.ForeignKey(Post, models.CASCADE)
    image = models.ImageField(upload_to='post/images/')


class Communities(models.Model):
    """
    Communities class
    """
    community = models.OneToOneField(to=User, on_delete=models.CASCADE, related_name='user_community')
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)


class Community(models.Model):
    """
    Community class
    """
    community = models.OneToOneField(to=User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    info = models.CharField(max_length=1000)

    # TODO: find default icon for communities
    avatar = models.ImageField(upload_to='avatars/communities', null=True, blank=True, default='avatars/users/0.png')

    def participants(self) -> list:
        """
        Get participants
        :return: list
        """
        users = []
        for com in Profile.communities():
            if self.community == com:
                users += Profile.user
        return users

    def amount_of_participants(self) -> int:
        """
        Get amount of participants
        :return: int
        """
        return len(self.participants())

    def posts(self):
        """
        Get community's posts
        """
        return Post.objects.filter(user=self.community)

    def amount_of_posts(self) -> int:
        """
        Get amount of posts
        :return: int
        """
        return len(self.posts())


class Participants(models.Model):
    """
    Participants class
    """
    user = models.OneToOneField(to=User, on_delete=models.CASCADE, related_name='user_in_community')
    community = models.OneToOneField(to=User, on_delete=models.CASCADE, related_name='community_of_user')


class Friend(models.Model):
    """
    Friend class
    """
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='1+')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='2+')


class FriendshipRequest(models.Model):
    """
    FriendshipRequest class
    """
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='3+')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='4+')
    already_sent = models.BooleanField(default=False)
