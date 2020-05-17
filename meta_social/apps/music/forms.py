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
        model = Music
        fields = ('audio_file', 'artist', 'title', )
        labels = {
            'audio_file': 'Аудио файл',
        }
