from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
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
    country = models.CharField(null=True, max_length=60)
    birth = models.DateField(null=True)
    show_email = models.BooleanField(default=False)

    def get_social_accounts(self):
        return [i.provider for i in self.user.socialaccount_set.all()]

    def get_social_data(self, provider):
        return self.user.socialaccount_set.filter(provider=provider)[0].extra_data

    def posts(self):
        return Posts.objects.filter(user=self.user)

    def amount_of_posts(self):
        return len(self.posts())

    def friends(self):
        return Friend.objects.filter(current_user=self.user)

    def amount_of_friends(self):
        return len(self.friends())

    def communities(self):
        return Communities.objects.filter(user=self.user)

    def amount_of_communities(self):
        return len(self.communities())

    def get_newsfeed(self):
        posts = []
        for friend in self.friends():
            posts.append(friend.posts())
        for com in self.communities():
            posts.append(com.posts())
        posts = sorted(posts, key=lambda x: x.date)
        return posts


class Posts(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    name_of_post = models.CharField(max_length=500)
    text = models.CharField(max_length=10000)
    date = models.DateField()


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
        return Posts.objects.filter(user=self.community)

    def amount_of_posts(self):
        return len(self.posts())


class Participants(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE, related_name='user_in_community')
    community = models.OneToOneField(to=User, on_delete=models.CASCADE, related_name='community_of_user')


class Friend(models.Model):
    users = models.ManyToManyField(User)
    current_user = models.ForeignKey(User, related_name='owner', null=True, on_delete=models.CASCADE)

    @classmethod
    def make_friend(cls, current_user, new_friend):
        friend, created = cls.objects.get_or_create(
            current_user=current_user
        )
        friend.users.add(new_friend)

    @classmethod
    def lose_friend(cls, current_user, new_friend):
        friend, created = cls.objects.get_or_create(
            current_user=current_user
        )
        friend.users.remove(new_friend)

