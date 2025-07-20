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
                html_parts = []
                # Render các field
                for field_name in self.display_fields or [f.name for f in obj._meta.fields]:
                    val = getattr(obj, field_name, "")

                    if isinstance(self.display_renderer, dict) and field_name in self.display_renderer:
                        renderer = self.display_renderer[field_name]

                        if callable(renderer):
                            html_parts.append(renderer(val, obj))
                        elif isinstance(renderer, str):
                            html_parts.append(renderer.format(val))
                        else:
                            html_parts.append(str(val))
                    else:
                        html_parts.append(
                            f'''
                            <div class="text-truncate small" title="{val}" style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                                <strong>{field_name.capitalize()}:</strong> {val}
                            </div>
                            '''
                        )

                content = ''.join(html_parts)

                # Card layout
                checkbox_id = f"id_{name}_{obj_id}"

                item_html = format_html(
                    '''
                    <div class="col-6 col-md-4 col-lg-3">
                        <label class="card h-100 shadow-sm" for="{checkbox_id}">
                            <div class="card-header d-flex justify-content-start align-items-center gap-2 py-1">
                                <input type="checkbox" id="{checkbox_id}" name="{name}" value="{value}" class="form-check-input" {checked}>
                                <span class="text-muted small">ID: {value}</span>
                            </div>
                            <div class="card-body p-2">
                                {content}
                            </div>
                        </label>
                    </div>
                    ''',
                    checkbox_id=checkbox_id,
                    name=name,
                    value=obj_id,
                    checked='checked' if selected else '',
                    content=mark_safe(content),
                )

                grid_items.append(item_html)

            return mark_safe(trigger + modal_header + ''.join(grid_items) + modal_footer)
