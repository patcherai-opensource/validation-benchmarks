from django import template
from django.template.base import Variable

register = template.Library()

@register.filter
def get_attr(obj, attr):
    """
    Get attribute from object using Django's Variable resolution.
    This mimics the vulnerable _property_resolver in dictsort (CVE-2021-45116).
    Allows accessing any attribute including private ones (underscore-prefixed).
    """
    try:
        # Using Variable resolution - vulnerable to accessing private attributes
        return getattr(obj, attr, '')
    except:
        return ''

@register.simple_tag
def resolve_attr(obj, attr):
    """
    Resolve attribute using Django's template Variable resolution.
    """
    try:
        var = Variable(f'obj.{attr}')
        ctx = {'obj': obj}
        return var.resolve(ctx)
    except:
        return getattr(obj, attr, '')
