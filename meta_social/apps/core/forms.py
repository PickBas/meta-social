"""
Meta social most used forms
"""

from django import forms

from .models import Developer


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


class DeveloperForm(forms.ModelForm):
    """
    Developer add form
    """
    class Meta:
        """
        Manage modelform
        """
        model = Developer
        fields = (
            'name',
            'role',
            'commits',
            'issiues',
            'phrase',
            'task_list',
            'contact',
        )

        labels = {
            'name': 'Имя Фамилия',
            'role': 'Роль в разработке',
            'commits': 'Количество коммитов',
            'issiues': 'Количество выполненных issues',
            'phrase': 'Афоризм/Лозунг/Фраза',
            'task_list': 'Список выполненных задач в проекте',
            'contact': 'email/site/socialpage',
        }
        widgets = {'task_list': forms.Textarea()}
