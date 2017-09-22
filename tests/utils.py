from __future__ import unicode_literals

import contextlib

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.compat import reverse
from rest_framework_simplejwt.settings import api_settings


def client_action_wrapper(action):
    def wrapper_method(self, *args, **kwargs):
        if self.view_name is None:
            raise ValueError('Must give value for `view_name` property')

        reverse_args = kwargs.pop('reverse_args', tuple())
        reverse_kwargs = kwargs.pop('reverse_kwargs', dict())
        query_string = kwargs.pop('query_string', None)

        url = reverse(self.view_name, args=reverse_args, kwargs=reverse_kwargs)
        if query_string is not None:
            url = url + '?{0}'.format(query_string)

        return getattr(self.client, action)(url, *args, **kwargs)

    return wrapper_method


class APIViewTestCase(TestCase):
    client_class = APIClient

    def authenticate_with_token(self, type, token):
        """
        Authenticates requests with the given token.
        """
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(type, token))

    view_name = None

    view_post = client_action_wrapper('post')
    view_get = client_action_wrapper('get')


@contextlib.contextmanager
def override_api_settings(**settings):
    old_settings = {}

    for k, v in settings.items():
        # Save settings
        try:
            old_settings[k] = api_settings.user_settings[k]
        except KeyError:
            pass

        # Install temporary settings
        api_settings.user_settings[k] = v

        # Delete any cached settings
        try:
            delattr(api_settings, k)
        except AttributeError:
            pass

    yield

    for k in settings.keys():
        # Delete temporary settings
        api_settings.user_settings.pop(k)

        # Restore saved settings
        try:
            api_settings.user_settings[k] = old_settings[k]
        except KeyError:
            pass

        # Delete any cached settings
        try:
            delattr(api_settings, k)
        except AttributeError:
            pass
