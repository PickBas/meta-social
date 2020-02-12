from django.contrib.auth.models import User
from django.db import models


class VK_Token(models.Model):
    access_token = models.CharField(max_length=500)
    userpage_id = models.CharField(max_length=500)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
