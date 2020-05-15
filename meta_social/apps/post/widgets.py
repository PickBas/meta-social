"""
Widgets module
"""

from django.forms.widgets import ClearableFileInput


class MyImageFieldWidget(ClearableFileInput):
    """
    Widget for nice ImageField
    """
    template_name = 'widgets/my_imagefield_widget.html'
