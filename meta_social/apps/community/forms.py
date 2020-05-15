"""
Meta social community forms
"""

from django import forms
from django_countries.fields import CountryField

from .models import Community


class EditCommunityForm(forms.ModelForm):
    """
    Community editing form
    """
    class Meta:
        model = Community
        fields = ('name', 'info', 'country',)
        widgets = {
            'info': forms.Textarea()
        }
        labels = {
            'name': 'Название',
            'info': 'Информация',
            'country': 'Страна',
        }


class CommunityCreateForm(forms.Form):
    """
    Form for creation community
    """
    name = forms.CharField(max_length=100)
    info = forms.CharField(max_length=1000)
    country = CountryField().formfield()


class UpdateCommunityAvatarForm(forms.ModelForm):
    """
    Form for updating community avatar
    """
    base_image = forms.ImageField(required=True)

    class Meta:
        """
        Class for representation in admin interface
        """
        model = Community
        fields = ('base_image', )
