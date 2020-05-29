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
        """
        Meta class. Getting fields.
        """
        model = Chat
        fields = ('base_image', )


class MessageMusicForm(forms.Form):
    """
    Form MessageMusicForm
    """
    music = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'style': 'display: none;'})
    )

    def __init__(self, *args: tuple, **kwargs: dict) -> None:
        """
        MessageMusicForm ctor
        :param args: args
        :param kwargs: kwargs
        """
        super().__init__(*args, **kwargs)
        self.fields['music'].label = ''


class MessageImageForm(forms.ModelForm):
    """
    Form for adding images to post
    """
    image = forms.ImageField()

    class Meta:
        """
        Meta class. Getting fields.
        """
        model = MessageImages
        fields = ('image',)

    def __init__(self, *args: tuple, **kwargs: dict) -> None:
        """
        MessageImageForm ctor
        :param args: args
        :param kwargs: kwargs
        """
        super(MessageImageForm, self).__init__(*args, **kwargs)
        self.fields['image'].label = ''
