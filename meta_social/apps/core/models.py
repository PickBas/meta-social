from django.db import models

# Create your models here.

class Developer(models.Model):
    """
    Model contains developer for about page

    :param name: Develpoer real name
    :param role: String contains role in project
    :param commits: Number of user commits
    :param issues: Number of issues
    :param phrase: Catch phrase
    """
    name =  models.CharField(null=True, max_length=100)
    role =  models.CharField(null=True, max_length=100)
    commits = models.IntegerField()
    issiues = models.IntegerField()
    phrase = models.CharField(blank=True, null=True, max_length=140)
    task_list = models.TextField()
    contact =  models.CharField(blank=True, null=True, max_length=100)
