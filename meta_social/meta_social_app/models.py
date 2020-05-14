"""
Modules module
"""

import sys, humanize

from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver
from django.utils import timezone
from django.core.files import File

from django_countries.fields import CountryField
from allauth.account.signals import user_signed_up
from allauth.socialaccount.models import SocialAccount
from urllib.request import urlopen
from tempfile import NamedTemporaryFile
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from apps.chat.models import Chat



