from django import template

register = template.Library()

@register.filter
def get_item(value, arg):
    """Retrieve an item from a dictionary."""
    try:
        return value[arg]
    except (KeyError, TypeError):
        return None