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
                    <i class="bi bi-list-check me-1"></i> Select Items
                </button>
                ''',
                modal_id
            )

            search_and_sort = f'''
                <div class="mb-3 d-flex justify-content-between align-items-center">
                    <input type="text" class="form-control form-control-sm w-50" placeholder="Search..." onkeyup="filterGridItems('{modal_id}', this.value)">
                    <select class="form-select form-select-sm w-auto" onchange="sortGridItems('{modal_id}', this.value)">
                        <option value="">Sort by...</option>
                        <option value="az">Name A-Z</option>
                        <option value="za">Name Z-A</option>
                    </select>
                </div>
            '''

            modal_header = format_html(
                '''
                <div class="modal fade" id="{id}" tabindex="-1" aria-labelledby="{id}Label" aria-hidden="true">
                  <div class="modal-dialog modal-xl modal-dialog-scrollable">
                    <div class="modal-content">
                      <div class="modal-header">
                        <h5 class="modal-title" id="{id}Label"><i class="bi bi-grid-3x3-gap me-2"></i>Select Items</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                      </div>
                      <div class="modal-body">
                        {search_sort}
                        <div class="row g-3">
                ''',
                id=modal_id,
                search_sort=mark_safe(search_and_sort)
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
                <script>
                function filterGridItems(modalId, keyword) {
                    keyword = keyword.toLowerCase();
                    const items = document.querySelectorAll('#' + modalId + ' .grid-item');
                    items.forEach(el => {
                        const label = el.getAttribute('data-label');
                        el.style.display = label.includes(keyword) ? '' : 'none';
                    });
                }

                function sortGridItems(modalId, direction) {
                    const container = document.querySelector('#' + modalId + ' .modal-body .row');
                    const items = Array.from(container.children);
                    items.sort((a, b) => {
                        const aLabel = a.getAttribute('data-label') || '';
                        const bLabel = b.getAttribute('data-label') || '';
                        return direction === 'az'
                            ? aLabel.localeCompare(bLabel)
                            : bLabel.localeCompare(aLabel);
                    });
                    items.forEach(item => container.appendChild(item));
                }
                </script>
            '''

            grid_items = []
            for obj in self.choices.queryset:
                obj_id = obj.pk
                selected = str(obj_id) in value

                if self.display_renderer and hasattr(obj, self.display_renderer):
                    render_func = getattr(obj, self.display_renderer)
                    content = render_func() if callable(render_func) else str(render_func)
                    label_text = str(obj)
                else:
                    fields = self.display_fields or [f.name for f in obj._meta.fields]
                    content_lines = []
                    label_text = ''
                    for field_name in fields:
                        val = getattr(obj, field_name)
                        val_display = str(val)
                        label_text += val_display + ' '
                        content_lines.append(
                            f'''
                            <div class="text-truncate small" title="{val_display}" style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                                <strong>{field_name.capitalize()}:</strong> {val_display}
                            </div>
                            '''
                        )
                    content = ''.join(content_lines)

                checkbox_id = f"id_{name}_{obj_id}"

                item_html = format_html(
                    '''
                    <div class="col-6 col-md-4 col-lg-3 grid-item" data-label="{label}">
                        <div class="card h-100 shadow-sm">
                            <label for="{checkbox_id}" class="w-100 h-100">
                                <div class="card-header d-flex justify-content-start align-items-center gap-2 py-1">
                                    <input type="checkbox" id="{checkbox_id}" name="{name}" value="{value}" class="form-check-input" {checked}>
                                    <span class="text-muted small">ID: {value}</span>
                                </div>
                                <div class="card-body p-2">
                                    {content}
                                </div>
                            </label>
                        </div>
                    </div>
                    ''',
                    checkbox_id=checkbox_id,
                    name=name,
                    value=obj_id,
                    checked='checked' if selected else '',
                    content=mark_safe(content),
                    label=label_text.lower()
                )

                grid_items.append(item_html)

            return mark_safe(trigger + modal_header + ''.join(grid_items) + modal_footer)
