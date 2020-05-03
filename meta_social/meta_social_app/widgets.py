from django.forms.widgets import ClearableFileInput
from django.template import loader
from django.utils.safestring import mark_safe


class MyImageFieldWidget(ClearableFileInput):
    template_name = 'widgets/my_imagefield_widget.html'
