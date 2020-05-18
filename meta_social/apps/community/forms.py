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
        """
        Manage modelform
        """
        model = Community
        fields = ('name', 'info', 'country', 'custom_url')
        widgets = {
            'info': forms.Textarea()
        }
        labels = {
            'name': 'Название',
            'info': 'Информация',
            'country': 'Страна',
            'custom_url': 'Ссылка',
        }


class CommunityCreateForm(forms.Form):
    """
    Form for creation community
    """
    name = forms.CharField(max_length=100, label='Название')
    info = forms.CharField(max_length=1000, label='О сообществе')
    country = CountryField().formfield(label='Страна')


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
