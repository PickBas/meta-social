"""
Meta social post models
"""

import sys
from io import BytesIO
from PIL import Image

from django.db import models
from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile

from music.models import Music


class Like(models.Model):
    """
    Like model

    :param date: like date
    :param user: like owner
    """
    date = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)


class Post(models.Model):
    """
    Post model

    :param user: ForeignKey to :class:`django.contrib.auth.models.User` model. Creator of post
    :param community: ForeignKey to :class:`community.models.Community` model. Creator of post
    :param text: text of post
    :param date: post creation date
    :param likes: ManyToManyField to :class:`post.models.Like`  model
    :param rt: ManyToManyField to :class:`django.contrib.auth.models.User`  model
    :param is_reposted: boolean field
    :param owner: ForeignKey to :class:`django.contrib.auth.models.User` model. Owner of post
    :param owner_community: ForeignKey to :class:`community.models.Community` model. Owner of post
    :param music: ManyToManyField to :class:`music.models.Music` model
    """
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True)
    community = models.ForeignKey(to='community.Community', on_delete=models.CASCADE, null=True)
    text = models.TextField()
    date = models.DateTimeField(auto_now=True, verbose_name='Дата создания')

    likes = models.ManyToManyField(Like, blank=True, related_name='likes')

    rt = models.ManyToManyField(User, blank=True, related_name='rt')

    is_reposted = models.BooleanField(default=False)

    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='owner')
    owner_community = models.ForeignKey(to='community.Community', on_delete=models.CASCADE, null=True, related_name='owner_community')

    music = models.ManyToManyField(Music)

    class Meta:
        """
        Class storing information for admin interface
        """
        verbose_name = 'Посты'
        verbose_name_plural = 'Посты'

    def __str__(self):
        """
        Returns a string representation of an object

        :return: text of post
        :rtype: str
        """
        return self.text

    def get_owner(self):
        """
        Returns owner of post

        :return: owner of post
        :rtype: :class:`community.models.Community` or :class:`user_profile.models.Profile`
        """
        return self.community if self.community else self.user.profile

    def get_owner_name(self):
        """
        Returns owner name

        :rtype: str
        """
        if self.community:
            return self.community.name
        return self.user.profile.get_name()

    def get_link(self):
        """
        Returns owner link

        :rtype: str
        """
        if self.community:
            return '/community/' + str(self.community.id) + '/'
        return '/accounts/profile/' + str(self.user.profile.custom_url) + '/'

    def get_images(self):
        """
        Returns images of post

        :rtype: django queryset
        """
        return PostImages.objects.filter(post=self).order_by('order')

    def get_images_count(self):
        """
        Returns the number of post images

        :rtype: int
        """
        return PostImages.objects.filter(post=self).count()

    def comments(self):
        """
        Returns all comments of post

        :rtype: django queryset
        """
        return Comment.objects.filter(post=self)

    def amount_of_comments(self):
        """
        Returns the number of post comments

        :rtype: int
        """
        return len(self.comments())

    def get_editors(self):
        """
        Returns all users, who can edit or delete post

        :rtype: :class:`django.contrib.auth.models.User`
        """
        editors = []
        if self.user:
            editors.append(self.user)
        if self.community:
            editors += self.community.admins.all()
        return editors

    def get_rt_count(self):
        """
        Returns amount of rts

        :rtype: int
        """
        return len(self.rt.all())


class PostImages(models.Model):
    """
    Posts images model

    :param post: ForeignKey to :class:`post.models.Post`
    :param from_user: ForeignKey to :class:`django.contrib.auth.models.User`
    :param image: ImageField
    :param order: order of image in post
    """
    post = models.ForeignKey(Post, models.CASCADE)
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to='post/images/', blank=True, null=True)
    order = models.IntegerField(default=0)

    def save(self):
        """
        Resize and compress image before save
        """
        img = Image.open(self.image)
        output = BytesIO()

        new_size = (720, (img.size[1] * 720) // img.size[0])

        img = img.resize(new_size, Image.ANTIALIAS)

        try:
            img.save(output, format='JPEG', quality=60)
            output.seek(0)
            self.image = InMemoryUploadedFile(output, 'ImageField', "{}.jpg".format(self.image.name.split('.')[0]), 'image/jpeg', sys.getsizeof(output), None)
        except OSError:
            img.save(output, format='PNG', quality=60)
            output.seek(0)
            self.image = InMemoryUploadedFile(output, 'ImageField', "{}.png".format(self.image.name.split('.')[0]), 'image/png', sys.getsizeof(output), None)

        super(PostImages, self).save()


class Comment(models.Model):
    """
    Post comments model

    :param date: comment creation date
    :param text: text of comment
    :param post: ForeignKey to :class:`post.models.Post`
    :param user: ForeignKey to :class:`django.contrib.auth.models.User`
    """
    date = models.DateTimeField(auto_now=True, verbose_name='Дата')
    text = models.CharField(max_length=500, verbose_name='Текст')

    post = models.ForeignKey(to=Post, on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)

    class Meta:
        """
        Class storing information for admin interface
        """
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарий'
