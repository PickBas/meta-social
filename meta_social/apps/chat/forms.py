"""
Meta social chat forms
"""

from django import forms
from .models import Chat


class UpdateChatAvatarForm(forms.ModelForm):
    """
    Form for updating community avatar
    """

    base_image = forms.ImageField(required=True)

    class Meta:
        model = Chat
        fields = ('base_image', )
