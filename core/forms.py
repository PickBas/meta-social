"""
Meta social most used forms
"""

from django import forms


class CropAvatarForm(forms.Form):
    """
    Form for cropping avatar

    :param x: x coordinate
    :param y: y coordinate
    :param width: width of rectangle
    :param hight: height of rectangle
    """
    x = forms.FloatField(widget=forms.HiddenInput())
    y = forms.FloatField(widget=forms.HiddenInput())
    width = forms.FloatField(widget=forms.HiddenInput())
    height = forms.FloatField(widget=forms.HiddenInput())
