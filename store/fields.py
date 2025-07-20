from django.db import models
from .widgets import GridSelectModalWidget

class GridSelectManyToManyField(models.ManyToManyField):
    def formfield(self, **kwargs):
        defaults = {'widget': GridSelectModalWidget}
        defaults.update(kwargs)
        return super().formfield(**defaults)
