"""
Meta social user profile forms
"""

from django import forms
from django.contrib.auth.models import User

from .models import Profile


class ProfileUpdateForm(forms.ModelForm):
    """
    ProfileUpdateForm class. Used for updating user profile
    """
    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)

        for key in self.fields:
            self.fields[key].required = False

    class Meta:
        model = Profile
        fields = ('job', 'study', 'biography', 'gender', 'country', 'birth', 'custom_url', 'show_email')
        widgets = {
            'birth': forms.DateInput(attrs={'type': 'date'})
        }
        labels = {
            'custom_url': 'Ссылка',
            'job': 'Работа',
            'study': 'Учеба',
            'biography': 'Биография',
            'gender': 'Пол',
            'country': 'Страна',
            'birth': 'Дата рождения',
            'show_email': 'Отображать почту',
        }


class UserUpdateForm(forms.ModelForm):
    """
    Form for changing first and last name of user
    """
    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class UpdateAvatarForm(forms.ModelForm):
    """
    Form for updating user avatar
    """
    base_image = forms.ImageField(required=True)

    class Meta:
        model = Profile
        fields = ('base_image', )
