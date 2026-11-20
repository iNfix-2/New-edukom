import bleach
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def clean_content(value):
    return mark_safe(bleach.clean(value or '', tags={'p', 'br', 'strong', 'b', 'em', 'i', 'ul', 'ol', 'li', 'h2', 'h3', 'h4', 'blockquote', 'a'}, attributes={'a': ['href', 'title']}, protocols={'https', 'http', 'mailto'}, strip=True))
