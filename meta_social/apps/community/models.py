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
    posts = models.ManyToManyField(Post, 'posts_com')
    base_image = models.ImageField(upload_to='avatars/communities', default='avatars/users/0.png')
    image = models.ImageField(upload_to='avatars/communities', default='avatars/users/0.png')
    country = CountryField(null=True)

    def get_posts(self):
        return reversed(self.posts.all())
