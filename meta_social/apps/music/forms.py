"""
Meta social music forms
"""

from django import forms
from .models import Music


class UploadMusicForm(forms.ModelForm):
    """
    Form for upload music
    """
    class Meta:
        """
        Meta class. Getting fields.
        """
        model = Music
        fields = ('audio_file', 'artist', 'title', )
        labels = {
            'audio_file': 'Аудио файл',
        }
        widgets = {
            'audio_file': forms.FileInput(attrs={'accept': 'audio/*'})
        }
