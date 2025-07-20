from django import forms
from django.utils.safestring import mark_safe
from django.utils.html import format_html

class GridSelectModalWidget(forms.CheckboxSelectMultiple):
    class Media:
        css = {
            'all': [
                'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
                'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css'
            ]
        }
        js = [
            'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js'
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
            <div class="modal fade" id="{}" tabindex="-1" aria-labelledby="{}Label" aria-hidden="true">
              <div class="modal-dialog modal-xl modal-dialog-scrollable">
                <div class="modal-content">
                  <div class="modal-header">
                    <h5 class="modal-title" id="{}Label"><i class="bi bi-list-check me-1"></i>Chọn mục</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                  </div>
                  <div class="modal-body">
            ''',
            modal_id, modal_id, modal_id
        )

        modal_footer = '''
                  </div>
                  <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Đóng</button>
                  </div>
                </div>
              </div>
            </div>
        '''

        grid_items = []
        for option in self.choices:
            obj = option[1]
            obj_id = option[0]
            selected = str(obj_id) in value

            content_html = self.render_fields(obj)

            item_html = format_html(
                '''
                <div class="col-6 col-md-4 col-lg-3">
                    <label class="grid-option position-relative d-block border rounded p-2 bg-light text-start h-100">
                        <input type="checkbox" name="{name}" value="{value}" class="form-check-input position-absolute top-0 start-0 m-2" {checked}>
                        {content}
                        <i class="bi bi-check-circle-fill text-primary position-absolute top-0 end-0 m-2" style="font-size: 1.2rem; {show_check}"></i>
                    </label>
                </div>
                ''',
                name=name,
                value=obj_id,
                checked='checked' if selected else '',
                content=content_html,
                show_check='' if selected else 'display: none;'
            )
            grid_items.append(item_html)

        grid_html = '<div class="row g-3 grid-select">' + '\n'.join(grid_items) + '</div>'
        return mark_safe(trigger + modal_header + grid_html + modal_footer)

    def render_fields(self, obj):
        fields_to_show = [
            f for f in obj._meta.fields
            if f.name not in ['id', 'pk'] and not f.is_relation
        ]

        rows = []
        for field in fields_to_show:
            field_name = field.name
            value = getattr(obj, field_name, '')

            if hasattr(value, 'url'):
                file_url = value.url
                if str(file_url).lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                    rows.append(format_html(
                        '<img src="{}" alt="{}" class="img-fluid rounded mb-2" style="max-height:120px;">',
                        file_url, field_name
                    ))
                elif str(file_url).lower().endswith('.mp4'):
                    rows.append(format_html(
                        '<video controls class="w-100 rounded mb-2" style="max-height:120px;"><source src="{}" type="video/mp4"></video>',
                        file_url
                    ))
                else:
                    rows.append(format_html(
                        '<div class="small"><strong>{}:</strong> <a href="{}" target="_blank">File</a></div>',
                        field.verbose_name, file_url
                    ))
            else:
                # Format cho boolean / ngày tháng / văn bản
                if isinstance(value, bool):
                    icon = 'bi-check-lg text-success' if value else 'bi-x-lg text-danger'
                    rows.append(format_html(
                        '<div class="small"><strong>{}:</strong> <i class="bi {}"></i></div>',
                        field.verbose_name, icon
                    ))
                else:
                    rows.append(format_html(
                        '<div class="small text-muted"><strong>{}:</strong> {}</div>',
                        field.verbose_name,
                        value if value else '<span class="text-muted">—</span>'
                    ))

        return mark_safe(''.join(rows) if rows else f'<div class="text-muted">{str(obj)}</div>')
