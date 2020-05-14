

class UploadMusicForm(forms.ModelForm):
    """
    Form for upload music
    """
    class Meta:
        model = Music
        fields = ('audio_file', 'artist', 'title', )