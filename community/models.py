"""
Meta social community models
"""

from django.db import models
from django.contrib.auth.models import User

from post.models import Post


class Community(models.Model):
    """
    Community model

    :param users: all users of community. ManyToManyField to :class:`django.contrib.auth.models.User` model
    :param admins: all admins of community. ManyToManyField to :class:`django.contrib.auth.models.User` model
    :param owner: owner of community. ForeignKey to :class:`django.contrib.auth.models.User` model
    :param name: community name
    :param info: information about community
    :param custom_url: editable community url
    :param posts: all posts of community. ManyToManyField to :class:`post.models.Post` model
    :param base_image: not cropped avatar of community
    :param image: cropped avatar of community
    """
    users = models.ManyToManyField(to=User, related_name='users')
    admins = models.ManyToManyField(to=User, related_name='admins')
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True)
    info = models.CharField(max_length=1000, null=True)

    custom_url = models.CharField(max_length=50,
                                  default='',
                                  unique=True,
                                  help_text='Required. 50 characters or fewer. Letters, digits and @/./+/-/_ only.',
                                  validators=[User.username_validator],
                                  error_messages={
                                      'unique': 'A user with that username already exists.',
                                      'invalid': 'Invalid url'
                                  }, )

    posts = models.ManyToManyField(Post, 'posts_com')
    base_image = models.ImageField(upload_to='avatars/communities', default='avatars/users/unknown_profile.jpg')
    image = models.ImageField(upload_to='avatars/communities', default='avatars/users/unknown_profile.jpg')

    def get_posts(self):
        """
        Method for getting all posts of community

        :rtype: Django queryset
        """
        return reversed(self.posts.all())
