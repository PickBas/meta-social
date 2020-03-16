"""
Modules module
"""


from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django_countries.fields import CountryField


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

    avatar = models.ImageField(upload_to='avatars/users/', null=True, blank=True, default='avatars/users/0.png')
    job = models.CharField(null=True, max_length=100)
    biography = models.CharField(max_length=500, null=True)

    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True)
    country = CountryField()
    birth = models.DateField(null=True)
    show_email = models.BooleanField(default=False)

    last_logout = models.DateTimeField(default=timezone.now, auto_now=False, auto_now_add=False)
    last_act = models.DateTimeField(default=timezone.now, auto_now=False, auto_now_add=False)

    blacklist = models.ManyToManyField(User, 'blacklist')

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
        return Post.objects.filter(user=self.user)

    def amount_of_posts(self) -> int:
        """
        Get amount of posts
        :return: int
        """
        return len(self.posts())

    def friends(self) -> list:
        """
        Get friends
        :return: dict
        """
        # TODO: Сделать всё в один словарь
        friend_items1 = Friend.objects.filter(from_user=self.user)
        friend_items2 = Friend.objects.filter(to_user=self.user)

        return [friend_items1, friend_items2]

    def friendship_requests(self):
        """
        Get friendship requests
        """
        return FriendshipRequest.objects.filter(to_user=self.user)

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
            posts += friend.profile.posts()
        for com in self.communities():
            posts += com.posts()
        posts = sorted(posts, key=lambda x: x.date, reverse=True)
        return posts


class Post(models.Model):
    """
    Post class
    """
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    name_of_post = models.CharField(max_length=200)
    text = models.TextField()
    date = models.DateTimeField(default=timezone.now)

    def publish(self) -> None:
        """
        Publish a post
        :return: None
        """
        self.save()

    def __str__(self):
        return self.name_of_post


class Communities(models.Model):
    """
    Communities class
    """
    community = models.OneToOneField(to=User, on_delete=models.CASCADE, related_name='user_community')
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs) -> None:
    """
    creating user profile
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs) -> None:
    """
    Saving user profile
    """
    instance.profile.save()


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
