"""
Meta social community models
"""

from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField

from post.models import Post


class Community(models.Model):
    """
    Community model
    """
    users = models.ManyToManyField(to=User, related_name='users')
    admins = models.ManyToManyField(to=User, related_name='admins')
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True)
    info = models.CharField(max_length=1000, null=True)

    custom_url = models.CharField(max_length=50, default='')

    base_image = models.ImageField(upload_to='avatars/communities', default='avatars/users/0.png')
    image = models.ImageField(upload_to='avatars/communities', default='avatars/users/0.png')

    country = CountryField(null=True)

    def posts(self):
        """
        Get community's posts
        """
        return Post.objects.filter(community=self)[::-1]

    def amount_of_posts(self) -> int:
        """
        Get amount of posts
        :return: int
        """
        return len(self.posts())
