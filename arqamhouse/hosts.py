from django.conf import settings
from django_hosts import patterns, host

host_patterns = patterns('',
    host(r'www', settings.ROOT_URLCONF, name='www'),
    host(r'(\w+)', settings.ROOT_URLCONF, name='wildcard'),
    # host(r'(?P<username>\w+).house', 'houses.urls', name='house-dashboard'),
    # host(r'house', 'houses.urls', name='house-dashboard'),
)
