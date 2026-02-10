from django import template
from django.template import Variable

register = template.Library()


def _property_resolver(arg):
    """
    Resolve a property path for sorting or filtering gallery items.
    Uses Django's template Variable system for flexible attribute access.
    """
    try:
        arg = float(arg)
    except ValueError:
        pass
    
    if isinstance(arg, float):
        return lambda item: arg
    else:
        def resolve(item):
            try:
                var = Variable(arg)
                return var.resolve({'item': item})
            except:
                return ''
        return resolve


@register.filter
def getattribute(obj, attr_path):
    """
    Template filter to resolve attributes using dot notation.
    Used for displaying field values in gallery items.
    """
    if not attr_path:
        return ''
    
    resolver = _property_resolver("item." + attr_path)
    return resolver(obj)
