from django import template
from django.template.defaultfilters import _property_resolver

register = template.Library()


@register.filter
def attr(obj, attribute_name):
    """
    Dynamic attribute accessor for report generation.
    Allows flexible field access for custom reports.
    """
    try:
        resolver = _property_resolver(attribute_name)
        result = resolver(obj)
        return result
    except Exception:
        return ''
