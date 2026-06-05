from django import template

register = template.Library()

@register.filter
def mask_username(username):
    if len(username) <= 1:
        return username
    return username[0] + '**'

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, 0)
