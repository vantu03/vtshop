# widgets.py
from django import forms
from django.utils.safestring import mark_safe
from .models import Image

class ImageMultiSelectWidget(forms.SelectMultiple):
    def render(self, name, value, attrs=None, renderer=None):
        html = '<div style="margin-bottom:10px">'
        if value:
            try:
                images = Image.objects.filter(pk__in=value)
                for image in images:
                    html += f'<img src="{image.image.url}" height="60" style="margin:2px;border:1px solid #ccc;" />'
            except:
                pass
        html += '</div>'
        html += super().render(name, value, attrs, renderer)
        return mark_safe(html)
