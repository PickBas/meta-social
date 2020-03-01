from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)

    def get_social_accounts(self):
        return [i.provider for i in self.user.socialaccount_set.all()]

    def get_social_data(self, provider):
        return self.user.socialaccount_set.filter(provider=provider)[0].extra_data


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
