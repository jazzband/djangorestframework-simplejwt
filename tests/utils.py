import contextlib
import json

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import Client, TestCase
from django.test.utils import override_settings

from ninja_jwt.compat import reverse


def client_action_wrapper(action):
    def wrapper_method(self, *args, url=None, **kwargs):
        if not url and self.view_name is None:
            raise ValueError("Must give value for `view_name` property")

        reverse_args = kwargs.pop("reverse_args", tuple())
        reverse_kwargs = kwargs.pop("reverse_kwargs", dict())
        query_string = kwargs.pop("query_string", None)

        if self.header:
            kwargs.update(self.header)
            self.header.clear()

        _url = url or reverse(self.view_name, args=reverse_args, kwargs=reverse_kwargs)
        if query_string is not None:
            _url = _url + "?{0}".format(query_string)

        response = getattr(self.client, action)(_url, *args, **kwargs)
        try:
            response.data = json.loads(response.content)
        except (Exception,):
            pass
        return response

    return wrapper_method


class APIViewTestCase:
    client_class = Client
    header = dict()

    def setUp(self):
        self.client = self.client_class()

    def authenticate_with_token(self, type, token):
        """
        Authenticates requests with the given token.
        """
        self.header = dict(HTTP_AUTHORIZATION="{} {}".format(type, token))

    view_name = None

    view_post = client_action_wrapper("post")
    view_get = client_action_wrapper("get")


def override_api_settings(**new_settings):
    from django.conf import settings

    old_settings = getattr(settings, "NINJA_JWT", {})
    combined_settings = dict(old_settings)
    combined_settings.update(new_settings)
    return override_settings(SIMPLE_JWT=combined_settings)


class MigrationTestCase:
    migrate_from = None
    migrate_to = None

    def setUp(self):
        self.migrate_from = [self.migrate_from]
        self.migrate_to = [self.migrate_to]

        # Reverse to the original migration
        executor = MigrationExecutor(connection)
        # executor.migrate(self.migrate_from)

        old_apps = executor.loader.project_state(self.migrate_from).apps
        self.setUpBeforeMigration(old_apps)

        # Run the migration to test
        executor.loader.build_graph()
        # executor.migrate(self.migrate_to)

        self.apps = executor.loader.project_state(self.migrate_to).apps

    def setUpBeforeMigration(self, apps):
        pass
