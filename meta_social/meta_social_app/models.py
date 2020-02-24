from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, default='avatars/0.png')
    country = models.CharField(null=True, max_length=60)
    birth_day = models.DateField(null=True)
    status = models.CharField(max_length=500, null=True)
    last_time_online = models.DateTimeField(null=True)

    def good_date(self, date):
        return '{}.{}.{} {}:{}'.format(date.day, date.month, date.year, date.hour, date.minute)

    def good_joined_date(self):
        return self.good_date(self.user.date_joined)

    def good_login_date(self):
        return self.good_date(self.user.last_login)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
