from django import template

register = template.Library()

@register.filter(name='attendance_status_class')
def attendance_status_class(status):
    """
    Maps attendance status to Tailwind CSS classes for styling.
    """
    status_classes = {
        'PRESENT': 'bg-green-100 text-green-700',
        'ABSENT': 'bg-red-100 text-red-700',
        'PENDING': 'bg-yellow-100 text-yellow-700',
        'CANCELLED': 'bg-gray-100 text-gray-700',
    }

    return status_classes.get(status, 'bg-gray-100 text-gray-700')  # Default to gray if unknown

@register.filter(name='attendance_status_icon')
def attendance_status_icon(status):
    """
    Maps attendance status to icon classes.
    """
    icon_classes = {
        'PRESENT': 'bx bx-check text-green-700',
        'ABSENT': 'bx bx-x text-red-700',
        'PENDING': 'bx bx-time text-yellow-700',
        'CANCELLED': 'bx bx-ban text-gray-700',
    }
    return icon_classes.get(status, 'bx bx-question-mark text-gray-700') # default to question mark icon if unknown