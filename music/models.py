"""
Meta social music models
"""

from django.db import models
from django.contrib.auth.models import User


# from user_profile.models import Profile

class Music(models.Model):
    """
    Music model

    :param audio_file: music file
    :param artist: music's artist
    :param title: music's title
    """
    # user = models.ForeignKey(to=User, on_delete=models.CASCADE)

    audio_file = models.FileField(upload_to='music')

    artist = models.CharField(default='Автор', max_length=100, verbose_name='Автор')
    title = models.CharField(default='Название', max_length=100, verbose_name='Название')

    class Meta:
        """
        Class storing information for admin interface
        """
        verbose_name = 'Музыка'
        verbose_name_plural = 'Музыка'
