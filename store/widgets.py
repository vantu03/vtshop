from django import forms
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.db import models

class GridSelectManyToManyField(models.ManyToManyField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {
            'widget': GridSelectManyToManyField.GridSelectModalWidget()
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)

    class GridSelectModalWidget(forms.CheckboxSelectMultiple):
        class Media:
            css = {'all': []}
            js = []

        def render(self, name, value, attrs=None, renderer=None):
            value = set(map(str, value or []))
            wrapper_id = f"gridSelect_{name}"

            # Nút toggle gọn nhẹ dùng thẻ <details>
            trigger = format_html(
                f'''
                <details id="{wrapper_id}" class="module aligned">
                  <summary class="button default">Chọn mục</summary>
                  <div class="form-row">
                '''
            )

            # Danh sách checkbox dạng grid
            grid_items = []
            for obj in self.choices.queryset:
                obj_id = obj.pk
                selected = str(obj_id) in value

                content_lines = []
                for field in obj._meta.fields:
                    verbose = field.verbose_name.capitalize()
                    val = getattr(obj, field.name)
                    content_lines.append(f"<strong>{verbose}:</strong> {val}")

                label_html = "<br>".join(content_lines)

                item_html = format_html(
                    '''
                    <div class="inline-group">
                        <label class="vCheckboxLabel">
                            <input type="checkbox" name="{name}" value="{value}" class="form-checkbox" {checked}>
                            {label}
                        </label>
                    </div>
                    ''',
                    name=name,
                    value=obj_id,
                    checked='checked' if selected else '',
                    label=mark_safe(label_html),
                )
                grid_items.append(item_html)

            close_wrapper = '''
                  </div>
                </details>
            '''

            return mark_safe(trigger + ''.join(grid_items) + close_wrapper)