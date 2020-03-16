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

    def amount_of_posts(self):
        return len(self.posts())

    def friends(self):
        # TODO: Сделать всё в один словарь
        friend_items1 = Friend.objects.filter(from_user=self.user)
        friend_items2 = Friend.objects.filter(to_user=self.user)

        return [friend_items1, friend_items2]

    def friendship_requests(self):
        return FriendshipRequest.objects.filter(to_user=self.user)

    def amount_of_friends(self):
        return len(self.friends())

    def communities(self):
        return Communities.objects.filter(user=self.user)

    def amount_of_communities(self):
        return len(self.communities())

    def get_newsfeed(self):
        posts = []
        for friend in self.friends():
            posts += friend.profile.posts()
        for com in self.communities():
            posts += com.posts()
        posts = sorted(posts, key=lambda x: x.date, reverse=True)
        return posts


class Post(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    name_of_post = models.CharField(max_length=200)
    text = models.TextField()
    date = models.DateTimeField(default=timezone.now)

    def publish(self):
        self.save()

    def __str__(self):
        return self.name_of_post


class Communities(models.Model):
    community = models.OneToOneField(to=User, on_delete=models.CASCADE, related_name='user_community')
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Community(models.Model):
    community = models.OneToOneField(to=User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    info = models.CharField(max_length=1000)

    # TODO: find default icon for communities
    avatar = models.ImageField(upload_to='avatars/communities', null=True, blank=True, default='avatars/users/0.png')

    def participants(self):
        users = []
        for com in Profile.communities():
            if self.community == com:
                users += Profile.user
        return users

    def amount_of_participants(self):
        return len(self.participants())

    def posts(self):
        return Post.objects.filter(user=self.community)

    def amount_of_posts(self):
        return len(self.posts())


class Participants(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE, related_name='user_in_community')
    community = models.OneToOneField(to=User, on_delete=models.CASCADE, related_name='community_of_user')


class Friend(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='1+')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='2+')


class FriendshipRequest(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='3+')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='4+')
    already_sent = models.BooleanField(default=False)
