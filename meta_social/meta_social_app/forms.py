'''
Forms module
'''


from django import forms
from django.contrib.auth.models import User
from django.core.validators import ValidationError

from PIL import Image
from .models import Profile, Post, PostImages, Music, Community
from crispy_forms.helper import FormHelper
from django_countries.fields import CountryField

from django.utils.safestring import mark_safe
from .widgets import MyImageFieldWidget

