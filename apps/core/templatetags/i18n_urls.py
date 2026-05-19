"""
Template tags for i18n-aware URL translation.

Usage in templates:
    {% load i18n_urls %}
    {% translate_url request.path 'es' as es_url %}
    {{ es_url }}
"""

from django import template


from django.urls import translate_url as django_translate_url

register = template.Library()


@register.simple_tag
def translate_url(path, language_code):
    """
    Translate a URL path to the equivalent path in the given language.

    Uses Django's built-in translate_url utility which handles
    stripping/adding language prefixes from i18n_patterns URLs.
    """

    return django_translate_url(path, language_code)
