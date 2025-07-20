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

        # Nút mở modal
        trigger = format_html(
            '''
            <button type="button" class="btn btn-outline-primary mb-2" data-bs-toggle="modal" data-bs-target="#{}">
                <i class="bi bi-list-check me-1"></i> Chọn mục
            </button>
            ''',
            modal_id
        )

        # Modal header/footer
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

        # Danh sách chọn dạng lưới
        grid_start = '<div class="row g-3 grid-select">'
        grid_items = []

        for option in self.choices:
            obj = option[1]
            obj_id = option[0]
            selected = str(obj_id) in value

            label = str(obj)

            item_html = format_html(
                '''
                <div class="col-6 col-md-4 col-lg-3">
                    <label class="grid-option position-relative d-block border rounded p-2 bg-light text-center h-100">
                        <input type="checkbox" name="{}" value="{}" class="form-check-input position-absolute top-0 start-0 m-2" {} />
                        {}
                        <div class="small mt-2 text-truncate">{}</div>
                        {}
                    </label>
                </div>
                ''',
                name,
                obj_id,
                'checked' if selected else '',
                '',
                label,
                '<i class="bi bi-check-circle-fill text-primary position-absolute top-0 end-0 m-2" style="font-size: 1.2rem;"></i>' if selected else ''
            )
            grid_items.append(item_html)

        grid_html = grid_start + '\n'.join(grid_items) + '</div>'
        return mark_safe(trigger + modal_header + grid_html + modal_footer)