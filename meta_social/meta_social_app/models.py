from django.contrib.auth.models import User
from django.db import models


class modelUser(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    # avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, default='avatars/0.png')
    country = models.CharField(null=True, max_length=60)
    birth_day = models.DateField(null=True)
    status = models.CharField(max_length=500, null=True)
