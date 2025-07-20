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
            css = {
                'all': ['admin/css/forms.css']  # dùng CSS có sẵn của admin
            }
            js = []  # JS sẽ inline để toggle modal

        def render(self, name, value, attrs=None, renderer=None):
            value = set(map(str, value or []))
            modal_id = f"gridSelectModal_{name}"

            # JS đơn giản để mở/đóng modal
            script = f'''
            <script>
                document.addEventListener("DOMContentLoaded", function () {{
                    const openBtn = document.getElementById("open_{modal_id}");
                    const modal = document.getElementById("{modal_id}");
                    const closeBtn = document.getElementById("close_{modal_id}");

                    openBtn.addEventListener("click", function () {{
                        modal.style.display = "block";
                    }});
                    closeBtn.addEventListener("click", function () {{
                        modal.style.display = "none";
                    }});
                    window.addEventListener("click", function(e) {{
                        if (e.target == modal) {{
                            modal.style.display = "none";
                        }}
                    }});
                }});
            </script>
            '''

            # Trigger button
            trigger = format_html(f'''
                <button type="button" class="button" id="open_{modal_id}">
                    Chọn mục
                </button>
            ''')

            # Modal structure (dùng class admin)
            modal_open = format_html(f'''
            <div id="{modal_id}" class="module" style="display:none; position:fixed; top:0; left:0;
                width:100%; height:100%; background:rgba(0,0,0,0.4); z-index:1000;">
                <div class="module" style="background:#fff; margin:5% auto; padding:20px; width:90%;
                    max-width:1000px; border-radius:8px; overflow:auto; max-height:90vh;">
                    <div class="form-row">
                        <h3>Chọn mục</h3>
                        <button type="button" class="button" id="close_{modal_id}" style="float:right;">Đóng</button>
                    </div>
                    <div class="form-row inline-group" style="display: flex; flex-wrap: wrap; gap: 16px;">
            ''')

            grid_items = []
            for obj in self.choices.queryset:
                obj_id = obj.pk
                selected = str(obj_id) in value

                content_lines = []
                for field in obj._meta.fields:
                    verbose = field.verbose_name.capitalize()
                    val = getattr(obj, field.name)
                    content_lines.append(f"<strong>{verbose}:</strong> {val}")

                content = "<br>".join(content_lines)

                item_html = format_html(
                    '''
                    <div class="inline-related" style="min-width: 220px; border: 1px solid #ddd; padding: 8px; border-radius: 4px;">
                        <label class="vCheckboxLabel">
                            <input type="checkbox" name="{name}" value="{value}" class="form-checkbox" {checked}>
                            {content}
                        </label>
                    </div>
                    ''',
                    name=name,
                    value=obj_id,
                    checked='checked' if selected else '',
                    content=mark_safe(content)
                )
                grid_items.append(item_html)

            modal_close = '''
                    </div>
                    <div class="form-row" style="text-align: right; margin-top: 10px;">
                        <button type="button" class="button" id="close_{modal_id}">OK</button>
                    </div>
                </div>
            </div>
            '''.replace('{modal_id}', modal_id)

            return mark_safe(script + trigger + modal_open + ''.join(grid_items) + modal_close)
