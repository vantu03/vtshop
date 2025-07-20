from django import forms
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.db import models

class GridSelectManyToManyField(models.ManyToManyField):
    def __init__(self, *args, display_fields=None, display_renderer=None, **kwargs):
        self.display_fields = display_fields
        self.display_renderer = display_renderer
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {
            'widget': self.GridSelectModalWidget(
                display_fields=self.display_fields,
                display_renderer=self.display_renderer,
            )
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)

    class GridSelectModalWidget(forms.CheckboxSelectMultiple):
        def __init__(self, display_fields=None, display_renderer=None, attrs=None):
            self.display_fields = display_fields
            self.display_renderer = display_renderer
            super().__init__(attrs)

        class Media:
            css = {
                'all': [
                    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
                    'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css',
                ]
            }
            js = [
                'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
            ]

        def render(self, name, value, attrs=None, renderer=None):
            value = set(map(str, value or []))
            modal_id = f"gridSelectModal_{name}"

            trigger = format_html(
                '''
                <button type="button" class="btn btn-outline-primary mb-2" data-bs-toggle="modal" data-bs-target="#{}">
                    <i class="bi bi-list-check me-1"></i> Chọn mục
                </button>
                ''',
                modal_id
            )

            modal_header = format_html(
                '''
                <div class="modal fade" id="{id}" tabindex="-1" aria-labelledby="{id}Label" aria-hidden="true">
                  <div class="modal-dialog modal-xl modal-dialog-scrollable">
                    <div class="modal-content">
                      <div class="modal-header">
                        <h5 class="modal-title" id="{id}Label"><i class="bi bi-grid-3x3-gap me-2"></i>Chọn mục</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Đóng"></button>
                      </div>
                      <div class="modal-body">
                        <div class="row g-3">
                ''',
                id=modal_id
            )

            modal_footer = '''
                        </div>
                      </div>
                      <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">OK</button>
                      </div>
                    </div>
                  </div>
                </div>
            '''

            grid_items = []
            for obj in self.choices.queryset:
                obj_id = obj.pk
                selected = str(obj_id) in value

                # Nếu có display_renderer → gọi hàm hiển thị custom
                if self.display_renderer and hasattr(obj, self.display_renderer):
                    render_func = getattr(obj, self.display_renderer)
                    if callable(render_func):
                        content = render_func()
                    else:
                        content = str(render_func)
                else:
                    # Nếu có display_fields → chỉ hiển thị những field đó
                    fields = self.display_fields or [f.name for f in obj._meta.fields]

                    content_lines = []
                    for field_name in fields:
                        field = obj._meta.get_field(field_name)
                        verbose = field.verbose_name.capitalize()
                        val = getattr(obj, field_name)
                        if isinstance(field, models.ImageField) and val:
                            val_display = f'<img src="{val.url}" class="img-fluid mb-1 rounded" style="max-height:100px;"><br>{val.name}'
                        else:
                            val_display = str(val)
                        content_lines.append(f"<strong>{verbose}:</strong> {val_display}")

                    content = "<br>".join(content_lines)

                item_html = format_html(
                    '''
                    <div class="col-6 col-md-4 col-lg-3">
                        <label class="border rounded p-2 d-block h-100 bg-light">
                            <input type="checkbox" name="{name}" value="{value}" class="form-check-input me-2" {checked}>
                            {content}
                        </label>
                    </div>
                    ''',
                    name=name,
                    value=obj_id,
                    checked='checked' if selected else '',
                    content=mark_safe(content),
                )
                grid_items.append(item_html)

            return mark_safe(trigger + modal_header + ''.join(grid_items) + modal_footer)
