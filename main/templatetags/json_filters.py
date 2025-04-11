from django import template
import json
from pprint import pformat

register = template.Library()

@register.filter
def pprint(value):
    """Pretty print JSON objects in templates"""
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            pass
    return pformat(value, indent=2)
