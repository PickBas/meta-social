"""
Meta social most used forms
"""

from django import forms


class CropAvatarForm(forms.Form):
    """
    Form for cropping avatar
    """
    x = forms.FloatField(widget=forms.HiddenInput())
    y = forms.FloatField(widget=forms.HiddenInput())
    width = forms.FloatField(widget=forms.HiddenInput())
    height = forms.FloatField(widget=forms.HiddenInput())
