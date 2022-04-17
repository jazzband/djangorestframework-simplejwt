.. _blacklist_app:

Blacklist app
=============

Simple JWT includes an app that provides token blacklist functionality.  To use
this app, include it in your list of installed apps in ``settings.py``:

.. code-block:: python

  # Django project settings.py

  ...

  INSTALLED_APPS = (
      ...
      'rest_framework_simplejwt.token_blacklist',
      ...
  )

Also, make sure to run ``python manage.py migrate`` to run the app's
migrations.

If the blacklist app is detected in ``INSTALLED_APPS``, Simple JWT will add any
generated refresh or sliding tokens to a list of outstanding tokens.  It will
also check that any refresh or sliding token does not appear in a blacklist of
tokens before it considers it as valid.

The Simple JWT blacklist app implements its outstanding and blacklisted token
lists using two models: ``OutstandingToken`` and ``BlacklistedToken``.  Model
admins are defined for both of these models.  To add a token to the blacklist,
find its corresponding ``OutstandingToken`` record in the admin and use the
admin again to create a ``BlacklistedToken`` record that points to the
``OutstandingToken`` record.

Alternatively, you can blacklist a token by creating a ``BlacklistMixin``
subclass instance and calling the instance's ``blacklist`` method:

.. code-block:: python

  from rest_framework_simplejwt.tokens import RefreshToken

  token = RefreshToken(base64_encoded_token_string)
  token.blacklist()

This will create unique outstanding token and blacklist records for the token's
"jti" claim or whichever claim is specified by the ``JTI_CLAIM`` setting.

In a ``urls.py`` file, you can also include a route for ``TokenBlackListView``:

.. code-block:: python

  from rest_framework_simplejwt.views import TokenBlacklistView

  urlpatterns = [
    ...
    path('api/token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    ...
  ]

It allows API users to blacklist tokens sending them to ``/api/token/blacklist/``, for example using curl:

.. code-block:: bash

  curl \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"refresh":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY1MDI5NTEwOCwiaWF0IjoxNjUwMjA4NzA4LCJqdGkiOiJhYTY3ZDUxNzkwMGY0MTEyYTY5NTE0MTNmNWQ4NDk4NCIsInVzZXJfaWQiOjF9.tcj1_OcO1BRDfFyw4miHD7mqFdWKxmP7BJDRmxwCzrg"}' \
    http://localhost:8000/api/token/blacklist/

The blacklist app also provides a management command, ``flushexpiredtokens``,
which will delete any tokens from the outstanding list and blacklist that have
expired.  You should set up a cron job on your server or hosting platform which
runs this command daily.
