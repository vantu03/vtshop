# fields.py
from django.db import models
from .widgets import GridSelectModalWidget

class GridSelectManyToManyField(models.ManyToManyField):
    def __init__(self, *args, display_fields=None, **kwargs):
        self.display_fields = display_fields or []
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {
            'widget': GridSelectModalWidget(display_fields=self.display_fields)
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)
