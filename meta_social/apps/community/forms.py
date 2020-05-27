"""
Meta social community forms
"""

from django import forms

from .models import Community


class EditCommunityForm(forms.ModelForm):
    """
    Community editing form
    """
    def __init__(self, *args, **kwargs):
        super(EditCommunityForm, self).__init__(*args, **kwargs)

        for key in self.fields:
            self.fields[key].required = True

    class Meta:
        """
        Manage modelform
        """
        model = Community
        fields = ('name', 'info', 'custom_url')
        widgets = {
            'info': forms.Textarea()
        }
        labels = {
            'name': 'Название',
            'info': 'Информация',
            'custom_url': 'Ссылка',
        }


class CommunityCreateForm(forms.Form):
    """
    Form for creation community
    """
    name = forms.CharField(max_length=100, label='Название')
    info = forms.CharField(max_length=1000, label='О сообществе')


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
