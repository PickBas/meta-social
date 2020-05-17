"""
Management utility to create superusers.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from user_profile.models import Profile
from allauth.account.models import EmailAddress
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


class Command(BaseCommand):
    help = 'Custom admin creating'

    def handle(self, *args, **options):
        username = ''
        password = ''
        email = ''

        while not username:
            username = input('Enter username: ')

            if not username:
                print('Error! Username is empty.\n')
            elif len(username) < 4:
                print('Error! Username must be longer than 4 symbols.\n')
                username = ''
            elif len(username) > 32:
                print('Error! Username too long (max 32 symbols).\n')
                username = ''
            elif User.objects.filter(username=username).exists():
                print('Error! Username already in use.\n')
                username = ''
        
        print()

        while not password:
            password = input('Enter password: ')

            if not password:
                print('Error! Password is empty.\n')
            elif len(password) < 4:
                print('Error! Password must be longer than 4 symbols.\n')
                password = ''
            elif len(password) > 32:
                print('Error! Password too long (max 32 symbols).\n')
                password = ''
            
            password_repeat = input('Please repeat the password: ')

            if password != password_repeat:
                print('Error! Passwords not equals.')
        
        print()

        while not email:
            email = input('Enter email: ')

            if not email:
                print('Error! Email is empty.\n')
            elif EmailAddress.objects.filter(email=email).exists():
                print('Error! Email already in use.\n')
                email = ''
            try:
                validate_email(email)
            except ValidationError:
                print('Error! Email is not correct.\n')
                email = ''

        user_item = User.objects.create_superuser(username, email, password)
        Profile.objects.create(user=user_item)
        EmailAddress.objects.create(
            verified=0,
            primary=1,
            user=user_item,
            email=email
        )

        print('\nSuperuser created successfully!\n')
