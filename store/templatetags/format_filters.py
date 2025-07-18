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

@register.simple_tag
def range_tag(*args):
    try:
        args = [int(a) for a in args]
        return range(*args)
    except Exception:
        return []

@register.filter
def smart_number(value):
    try:
        value = int(value)
        if value >= 1000000:
            return f"{value/1000000:.1f}tr"
        elif value >= 1000:
            return f"{value/1000:.1f}k"
        return str(value)
    except:
        return value


@register.simple_tag(takes_context=True)
def build_query(context, **kwargs):
    query = context['request'].GET.copy()

    for key, value in kwargs.items():
        if value is None:
            query.pop(key, None)
        else:
            query[key] = value

    encoded = query.urlencode()
    return f"?{encoded}"
