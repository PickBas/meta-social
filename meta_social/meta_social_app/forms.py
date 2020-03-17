from django import forms
from django.contrib.auth.models import User
from .models import Profile, Post, PostImages
from image_cropping import ImageCropWidget
from crispy_forms.helper import FormHelper


class ProfileUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)

        for key in self.fields:
            self.fields[key].required = False

    class Meta:
        model = Profile
        fields = ('job', 'biography', 'gender', 'country', 'birth')
        widgets = {
            'birth': forms.DateInput(attrs={'type': 'date', 'placeholder': 'Select a date'})
        }
        labels = {
            "job": "Работа",
            "biography": "Биография",
            "gender": "Пол",
            "country": "Страна",
            "birth": "Дата рождения"
        }


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class CropImageForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('cropping', 'image')
        widgets = {
            'image': ImageCropWidget,
        }


class PostForm(forms.ModelForm):
    text = forms.CharField(max_length=500)

    class Meta:
        model = Post
        fields = ('text',)
    
    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['text'].label = ''
        self.fields['text'].widget.attrs['width'] = '100%'
        self.fields['text'].widget.attrs['class'] = 'form-control'
        self.fields['text'].widget.attrs['aria-describedby'] = 'button-addon'


class PostImageForm(forms.ModelForm):
    image = forms.ImageField()

    class Meta:
        model = PostImages
        fields = ('image', )
    
    def __init__(self, *args, **kwargs):
        super(PostImageForm, self).__init__(*args, **kwargs)
        self.fields['image'].label = ''
