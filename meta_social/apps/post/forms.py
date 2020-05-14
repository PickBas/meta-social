

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
    Form for editing images of post
    """
    image = forms.ImageField(required=False, widget=MyImageFieldWidget)

    class Meta:
        model = PostImages
        fields = ('image', )
        
    def __init__(self, *args, **kwargs):
        super(EditPostImageForm, self).__init__(*args, **kwargs)
        self.fields['image'].label = ''