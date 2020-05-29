"""
Meta social chat forms
"""

from django import forms
from .models import Chat, MessageImages


class UpdateChatAvatarForm(forms.ModelForm):
    """
    Form for updating community avatar
    """

    base_image = forms.ImageField(required=True)

    class Meta:
        model = Chat
        fields = ('base_image', )


class MessageMusicForm(forms.Form):
    music = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'style': 'display: none;'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['music'].label = ''


class MessageImageForm(forms.ModelForm):
    """
    Form for adding images to post
    """
    image = forms.ImageField()

    class Meta:
        model = MessageImages
        fields = ('image',)

    def __init__(self, *args, **kwargs):
        super(MessageImageForm, self).__init__(*args, **kwargs)
        self.fields['image'].label = ''
