from django import template

register = template.Library()

@register.filter
def get_variation(image_field, key):
    try:
        variation = image_field.get_variation(key)
        return variation.url
    except Exception:
        return ''
