'''
Forms module
'''


from django import forms
from django.contrib.auth.models import User
from django.core.validators import ValidationError

from .models import Profile, Post, PostImages, Music
from image_cropping import ImageCropWidget
from crispy_forms.helper import FormHelper


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
        fields = ('job', 'study', 'biography', 'gender', 'country', 'birth', 'show_email')
        widgets = {
            'birth': forms.DateInput(attrs={'type': 'date'})
        }
        labels = {
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
        UserUpdateForm class
    """
    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class CropImageForm(forms.ModelForm):
    """
        Form for cropping image
    """
    class Meta:
        model = Profile
        fields = ('cropping', 'image')
        widgets = {
            'image': ImageCropWidget,
        }
    
    def __init__(self, *args, **kwargs):
        super(CropImageForm, self).__init__(*args, **kwargs)

        # TODO: Сделать нормальный размер кропинга
        self.fields['cropping'].widget.attrs['width'] = '100%'


class PostForm(forms.ModelForm):
    """
        Form for creation post
    """
    text = forms.CharField(max_length=500)

    class Meta:
        model = Post
        fields = ('text',)
    
    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['text'].label = ''
        self.fields['text'].widget = forms.Textarea()
        self.fields['text'].widget.attrs['width'] = '100%'
        self.fields['text'].widget.attrs['class'] = 'form-control'
        self.fields['text'].widget.attrs['rows'] = '1'
        self.fields['text'].widget.attrs['style'] = 'resize: none; padding: 0px 2px;'


class PostImageForm(forms.ModelForm):
    """
        Form for adding images to post
    """
    image = forms.ImageField()

    class Meta:
        model = PostImages
        fields = ('image', )
    
    def __init__(self, *args, **kwargs):
        super(PostImageForm, self).__init__(*args, **kwargs)
        self.fields['image'].label = ''


class UploadMusicForm(forms.ModelForm):
    class Meta:
        model = Music
        fields = ('audio_file', 'artist', 'title', )
