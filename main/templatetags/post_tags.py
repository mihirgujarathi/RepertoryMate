from django import template

register = template.Library()

def split(value, key):
    return value.split(key)

register.filter('split', split)