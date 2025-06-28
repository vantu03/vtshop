from django import template

register = template.Library()

@register.filter
def currency(value):
    try:
        return f"{int(value):,}".replace(",", ".") + "₫"
    except (ValueError, TypeError):
        return value

@register.filter
def smart_number(value):
    try:
        value = float(value)
        return int(value) if value.is_integer() else round(value, 1)
    except (ValueError, TypeError):
        return value
