'''
Forms module
'''


from django import forms
from django.contrib.auth.models import User
from django.core.validators import ValidationError

from PIL import Image
from .models import Profile, Post, PostImages, Music, Community
from crispy_forms.helper import FormHelper
from django_countries.fields import CountryField

from django.utils.safestring import mark_safe
from .widgets import MyImageFieldWidget


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


class UpdateAvatarForm(forms.ModelForm):
    base_image = forms.ImageField(required=True)

    class Meta:
        model = Profile
        fields = ('base_image', )


class CropAvatarForm(forms.Form):
    x = forms.FloatField(widget=forms.HiddenInput())
    y = forms.FloatField(widget=forms.HiddenInput())
    width = forms.FloatField(widget=forms.HiddenInput())
    height = forms.FloatField(widget=forms.HiddenInput())


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



class EditPostImageForm(forms.ModelForm):
    """
        Form for adding images to post
    """
    image = forms.ImageField(required=False, widget=MyImageFieldWidget)

    class Meta:
        model = PostImages
        fields = ('image', )
        
    def __init__(self, *args, **kwargs):
        super(EditPostImageForm, self).__init__(*args, **kwargs)
        self.fields['image'].label = ''


class UploadMusicForm(forms.ModelForm):
    class Meta:
        model = Music
        fields = ('audio_file', 'artist', 'title', )


class CommunityCreateForm(forms.Form):
    name = forms.CharField(max_length=100)
    info = forms.CharField(max_length=1000)
    country = CountryField().formfield()
