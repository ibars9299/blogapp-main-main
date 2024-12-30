from django import template

register = template.Library()

@register.filter
def isinstance(obj, class_str):
    """
    Template filter to check if an object is an instance of a class
    Usage: {% if item|isinstance:'Movie' %}
    """
    return obj.__class__.__name__ == class_str 