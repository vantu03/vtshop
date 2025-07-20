# fields.py
from django import forms
from django.utils.safestring import mark_safe
from django.utils.html import format_html


class DynamicMediaGridWidget(forms.CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, renderer=None):
        value = set(map(str, value or []))

        # Nhúng CSS & JS để tạo modal đơn giản & khung cuộn
        style = '''
        <style>
        .media-grid-wrapper {
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 10px;
            margin-top: 5px;
            background: #f9f9f9;
            max-height: 400px;
            overflow-y: auto;
        }
        .media-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        .media-item {
            cursor: pointer;
            position: relative;
            text-align: center;
            transition: transform 0.2s ease;
        }
        .media-item:hover {
            transform: scale(1.05);
        }
        .media-item img,
        .media-item video {
            width: 120px;
            height: 120px;
            object-fit: cover;
            border: 2px solid #ccc;
            border-radius: 6px;
            transition: border 0.2s ease;
        }
        .media-item input:checked + img,
        .media-item input:checked + video {
            border: 3px solid #007bff;
        }
        </style>
        '''

        # Optional: Toggle button
        toggle_button = f'''
        <script>
        function toggleMediaGrid_{name}() {{
            var grid = document.getElementById('media-grid-wrapper-{name}');
            if (grid.style.display === 'none') {{
                grid.style.display = 'block';
            }} else {{
                grid.style.display = 'none';
            }}
        }}
        </script>
        <a href="javascript:void(0)" onclick="toggleMediaGrid_{name}()" class="button">Chọn media</a>
        '''

        output = [style, toggle_button, f'<div id="media-grid-wrapper-{name}" class="media-grid-wrapper">', '<div class="media-grid">']

        for option in self.choices:
            obj = option[1]
            obj_id = option[0]
            selected = str(obj_id) in value

            media_html = self.render_media(obj)

            checkbox_html = format_html(
                '<label class="media-item">'
                '<input type="checkbox" name="{}" value="{}" {} style="display:none;">'
                '{}'
                '</label>',
                name,
                obj_id,
                'checked' if selected else '',
                media_html,
            )
            output.append(checkbox_html)

        output.append('</div></div>')
        return mark_safe('\n'.join(output))

    def render_media(self, obj):
        if hasattr(obj, 'image') and obj.image:
            return format_html(
                '<img src="{}" alt="{}">',
                obj.image.url,
                obj.image.name
            )
        elif hasattr(obj, 'video') and obj.video:
            return format_html(
                '<video controls><source src="{}" type="video/mp4"></video>',
                obj.video.url
            )
        else:
            return format_html(
                '<div style="width:120px;height:120px;display:flex;align-items:center;justify-content:center;background:#eee;">{}</div>',
                str(obj)
            )
