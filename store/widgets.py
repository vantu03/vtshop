# widgets.py
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

        output = [
            '<div class="border rounded p-3 bg-white" style="max-height: 400px; overflow-y: auto;">',
            '<div class="row g-3">'
        ]

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
            output.append(item_html)

        output.append('</div></div>')
        return mark_safe('\n'.join(output))

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
