from django import forms
from django.utils.safestring import mark_safe
from django.utils.html import format_html

class DynamicMediaGridWidget(forms.CheckboxSelectMultiple):
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
        modal_id = f"mediaModal_{name}"

        # Button trigger
        trigger = format_html(
            '''
            <button type="button" class="btn btn-outline-primary mb-2" data-bs-toggle="modal" data-bs-target="#{}">
                <i class="bi bi-images me-1"></i> Chọn media
            </button>
            ''',
            modal_id
        )

        # Start Modal
        modal_header = format_html(
            '''
            <div class="modal fade" id="{}" tabindex="-1" aria-labelledby="{}Label" aria-hidden="true">
              <div class="modal-dialog modal-xl modal-dialog-scrollable">
                <div class="modal-content">
                  <div class="modal-header">
                    <h5 class="modal-title" id="{}Label"><i class="bi bi-images me-1"></i>Chọn media</h5>
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

        # Media grid
        grid_start = '<div class="row g-3">'
        grid_items = []

        for option in self.choices:
            obj = option[1]
            obj_id = option[0]
            selected = str(obj_id) in value

            media_html = self.render_media(obj)
            label = str(obj)

            item_html = format_html(
                '''
                <div class="col-6 col-md-4 col-lg-3">
                    <label class="position-relative d-block border rounded p-2 bg-light text-center h-100">
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
                media_html,
                label,
                '<i class="bi bi-check-circle-fill text-primary position-absolute top-0 end-0 m-2" style="font-size: 1.2rem;"></i>' if selected else ''
            )
            grid_items.append(item_html)

        grid_html = grid_start + '\n'.join(grid_items) + '</div>'

        full_html = (
            trigger +
            modal_header +
            grid_html +
            modal_footer
        )

        return mark_safe(full_html)

    def render_media(self, obj):
        if hasattr(obj, 'image') and obj.image:
            return format_html(
                '<img src="{}" alt="{}" class="img-fluid rounded" style="max-height:120px; object-fit:cover;">',
                obj.image.url,
                obj.image.name
            )
        elif hasattr(obj, 'video') and obj.video:
            return format_html(
                '<video controls class="w-100 rounded" style="max-height:120px; object-fit:cover;">'
                '<source src="{}" type="video/mp4">'
                '</video>',
                obj.video.url
            )
        else:
            return format_html(
                '<div class="d-flex align-items-center justify-content-center bg-secondary text-white rounded" style="height: 120px;">'
                '<i class="bi bi-file-earmark" style="font-size: 2rem;"></i>'
                '</div>'
            )
