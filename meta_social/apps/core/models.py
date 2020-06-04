"""
Meta Social core models
"""

from django.db import models
from django.contrib.auth.models import User


class Developer(models.Model):
    """
    Model contains developer for about page

    :param name: Develpoer real name
    :param role: String contains role in project
    :param commits: Number of user commits
    :param issues: Number of issues
    :param phrase: Catch phrase
    """
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)

    gradient = models.CharField(max_length=50, default="aqua-gradient")
    name = models.CharField(null=True, max_length=100)
    role = models.CharField(null=True, max_length=100)
    phrase = models.CharField(blank=True, null=True, max_length=140)
    commits = models.IntegerField()
    task_list = models.TextField()
