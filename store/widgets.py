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
                'all': []
            }
            js = []

        def render(self, name, value, attrs=None, renderer=None):
            value = set(map(str, value or []))
            modal_id = f"gridSelectModal_{name}"

            # Inline CSS
            style = f'''
            <style>
                .grid-modal {{
                    display: none;
                    position: fixed;
                    z-index: 1000;
                    left: 0;
                    top: 0;
                    width: 100%;
                    height: 100%;
                    overflow: auto;
                    background-color: rgba(0, 0, 0, 0.4);
                }}
                .grid-modal-content {{
                    background-color: #fff;
                    margin: 5% auto;
                    padding: 20px;
                    border: 1px solid #888;
                    width: 90%;
                    max-width: 1000px;
                    border-radius: 10px;
                }}
                .grid-header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    border-bottom: 1px solid #ddd;
                    margin-bottom: 10px;
                }}
                .grid-body {{
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                    gap: 16px;
                    max-height: 60vh;
                    overflow-y: auto;
                }}
                .grid-item {{
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 10px;
                    background: #f9f9f9;
                }}
                .grid-item input[type="checkbox"] {{
                    margin-right: 8px;
                }}
                .grid-footer {{
                    margin-top: 10px;
                    text-align: right;
                }}
                .btn {{
                    padding: 6px 12px;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                }}
                .btn-primary {{
                    background-color: #007bff;
                    color: white;
                }}
                .btn-secondary {{
                    background-color: #6c757d;
                    color: white;
                }}
            </style>
            '''

            # Inline JS
            script = f'''
            <script>
                function openModal_{modal_id}() {{
                    document.getElementById("{modal_id}").style.display = "block";
                }}
                function closeModal_{modal_id}() {{
                    document.getElementById("{modal_id}").style.display = "none";
                }}
                window.addEventListener('click', function(event) {{
                    var modal = document.getElementById("{modal_id}");
                    if (event.target === modal) {{
                        modal.style.display = "none";
                    }}
                }});
            </script>
            '''

            # Trigger Button
            trigger = format_html(
                f'''
                <button type="button" class="btn btn-primary mb-2" onclick="openModal_{modal_id}()">
                    Chọn mục
                </button>
                '''
            )

            # Grid Items
            grid_items = []
            for obj in self.choices.queryset:
                obj_id = obj.pk
                selected = str(obj_id) in value

                content_lines = []
                for field in obj._meta.fields:
                    field_name = field.name
                    verbose = field.verbose_name.capitalize()
                    val = getattr(obj, field_name)
                    val_display = str(val)
                    content_lines.append(f"<strong>{verbose}:</strong> {val_display}")

                content = "<br>".join(content_lines)

                item_html = format_html(
                    '''
                    <div class="grid-item">
                        <label>
                            <input type="checkbox" name="{name}" value="{value}" class="form-check-input" {checked}>
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

            # Modal structure
            modal = format_html(
                f'''
                <div id="{modal_id}" class="grid-modal">
                  <div class="grid-modal-content">
                    <div class="grid-header">
                        <h5>Chọn mục</h5>
                        <button type="button" class="btn btn-secondary" onclick="closeModal_{modal_id}()">×</button>
                    </div>
                    <div class="grid-body">
                        {''.join(grid_items)}
                    </div>
                    <div class="grid-footer">
                        <button type="button" class="btn btn-secondary" onclick="closeModal_{modal_id}()">OK</button>
                    </div>
                  </div>
                </div>
                '''
            )

            return mark_safe(style + script + trigger + modal)
