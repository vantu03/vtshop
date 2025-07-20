from django import forms
from django.utils.safestring import mark_safe
from django.utils.html import format_html

class DynamicMediaGridWidget(forms.CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, renderer=None):
        value = set(map(str, value or []))

        style = '''
        <style>
        .media-grid-wrapper {
            border: 1px solid #d0d0d0;
            border-radius: 4px;
            padding: 10px;
            margin-top: 5px;
            background: #fff;
            max-height: 400px;
            overflow-y: auto;
        }

        .media-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
            gap: 10px;
        }

        .media-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            border: 1px solid #eee;
            padding: 5px;
            border-radius: 4px;
            transition: box-shadow 0.2s ease;
            background: #f9f9f9;
        }

        .media-item:hover {
            box-shadow: 0 0 5px #ccc;
        }

        .media-item img,
        .media-item video {
            width: 100%;
            height: auto;
            max-height: 120px;
            object-fit: cover;
            border-radius: 4px;
        }

        .media-item input {
            display: none;
        }

        .media-item input:checked + .media-preview {
            outline: 3px solid #0c6dfd;
        }

        .media-preview {
            display: block;
            width: 100%;
            height: 120px;
            object-fit: cover;
            border: 1px solid #ccc;
            border-radius: 4px;
        }

        .media-label {
            font-size: 12px;
            margin-top: 5px;
            color: #444;
            word-break: break-word;
        }
        </style>
        '''

        output = [style, '<div class="media-grid-wrapper">', '<div class="media-grid">']

        for option in self.choices:
            obj = option[1]
            obj_id = option[0]
            selected = str(obj_id) in value

            media_html = self.render_media(obj, selected)
            label = str(obj)

            item_html = format_html(
                '<label class="media-item">'
                '<input type="checkbox" name="{}" value="{}" {}>'
                '{}'
                '<div class="media-label">{}</div>'
                '</label>',
                name,
                obj_id,
                'checked' if selected else '',
                media_html,
                label
            )
            output.append(item_html)

        output.append('</div></div>')
        return mark_safe('\n'.join(output))

    def render_media(self, obj, selected):
        # Ưu tiên ảnh nếu có
        if hasattr(obj, 'image') and obj.image:
            return format_html(
                '<img src="{}" alt="{}" class="media-preview">',
                obj.image.url,
                obj.image.name
            )
        elif hasattr(obj, 'video') and obj.video:
            return format_html(
                '<video class="media-preview" controls>'
                '<source src="{}" type="video/mp4">'
                '</video>',
                obj.video.url
            )
        else:
            return format_html(
                '<div class="media-preview" style="display:flex;align-items:center;justify-content:center;background:#eee;">{}</div>',
                str(obj)
            )
