# fields.py
from django.db import models
from .widgets import DynamicMediaGridWidget

class MediaGridManyToManyField(models.ManyToManyField):
    def formfield(self, **kwargs):
        defaults = {'widget': DynamicMediaGridWidget}
        defaults.update(kwargs)
        return super().formfield(**defaults)
