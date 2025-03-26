from django import template
import re

register = template.Library()

@register.filter
def regex_replace(value, arg):
    """Replace regex pattern in string with a replacement."""
    try:
        # Expect arg as a string with pattern and replacement separated by a delimiter (e.g., '||')
        pattern, replacement = arg.split('||')
        return re.sub(pattern, replacement, str(value))
    except (ValueError, re.error):
        return str(value)  # Fallback to original value if parsing fails