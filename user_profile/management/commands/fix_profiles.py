"""
Management command
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from user_profile.models import Profile


class Command(BaseCommand):
    help = 'Creates profile for all users which haven\'t profile'

    def handle(self, *args, **kwargs):
        """
        Django requires this method
        """
        users_without_profile = [user for user in User.objects.all() if not Profile.objects.filter(user=user).exists()]
        u_length = len(users_without_profile)

        print('Users without profile: {}\n\n'.format(u_length))

        for user in users_without_profile:
            profile_item = Profile(
                user=user,
                custom_url=user.username,
            )

            profile_item.save()

            print('{}/{}'.format(u_length-1, u_length))
            u_length -= 1
