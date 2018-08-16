from django import template

register = template.Library()


@register.filter(name='to_hns')
def to_hns(value):
    if value is None or value == '':
        return ''
    return value / 1000000
