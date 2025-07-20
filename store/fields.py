# fields.py
from django.db import models
from .widgets import GridSelectModalWidget

class GridSelectManyToManyField(models.ManyToManyField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {
            'widget': GridSelectModalWidget()
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)
