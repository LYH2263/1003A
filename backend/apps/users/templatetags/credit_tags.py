from django import template

register = template.Library()

@register.filter
def mask_username(username):
    if len(username) <= 1:
        return username
    return username[0] + '**'
