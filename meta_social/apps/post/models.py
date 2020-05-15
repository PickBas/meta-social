"""
Meta social post models
"""

import sys
from io import BytesIO
from PIL import Image

from django.db import models
from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile


class Like(models.Model):
    """
    Like model
    """
    date = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)


class Post(models.Model):
    """
    Post model
    """
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True)
    community = models.ForeignKey(to='community.Community', on_delete=models.CASCADE, null=True)
    text = models.TextField()
    date = models.DateTimeField(auto_now=True, verbose_name='Дата создания')

    likes = models.ManyToManyField(Like, blank=True, related_name='likes')

    class Meta:
        """
        Class storing information for admin interface
        """
        verbose_name = 'Посты'
        verbose_name_plural = 'Посты'

    def __str__(self):
        """
        Returns a string representation of an object
        """
        return self.text

    def get_owner(self):
        """
        Returns owner of post
        """
        return self.community if self.community else self.user.profile

    def get_owner_name(self):
        """
        Returns owner name
        """
        if self.community:
            return self.community.name
        return self.user.profile.get_name()

    def get_link(self):
        """
        Returns owner link
        """
        if self.community:
            return '/community/' + str(self.community.id) + '/'
        return '/accounts/profile/' + str(self.user.id) + '/'

    def get_images(self):
        """
        Returns images of post
        """
        return PostImages.objects.filter(post=self).order_by('order')

    def get_images_count(self):
        """
        Returns the number of post images
        """
        return PostImages.objects.filter(post=self).count()

    def comments(self):
        """
        Returns all comments of post
        """
        return Comment.objects.filter(post=self)

    def amount_of_comments(self):
        """
        Returns the number of post comments
        """
        return len(self.comments())

    def get_editors(self):
        """
        Returns all users, who can edit or delete post
        """
        editors = []
        if self.user:
            editors.append(self.user)
        return editors


class PostImages(models.Model):
    """
    Posts images model
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
