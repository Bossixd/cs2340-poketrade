from django import template

register = template.Library()


@register.filter
def extract_card_id(url):

    if not isinstance(url, str):
        return ''
    try:

        start_index = url.index('?id=') + len('?id=')

        end_index = url.index('&from', start_index)
        return url[start_index:end_index]
    except ValueError:

        return ''
