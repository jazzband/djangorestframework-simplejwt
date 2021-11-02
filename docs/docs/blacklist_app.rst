.. _blacklist_app:

Blacklist app
=============

Ninja JWT includes an app that provides token blacklist functionality.  To use
this app, include it in your list of installed apps in ``settings.py``:

.. code-block:: python

  # Django project settings.py

  ...

  INSTALLED_APPS = (
      ...
      'ninja_jwt.token_blacklist',
      ...
  )

Also, make sure to run ``python manage.py migrate`` to run the app's
migrations.

If the blacklist app is detected in ``INSTALLED_APPS``, Ninja JWT will add any
generated refresh or sliding tokens to a list of outstanding tokens.  It will
also check that any refresh or sliding token does not appear in a blacklist of
tokens before it considers it as valid.

The Ninja JWT blacklist app implements its outstanding and blacklisted token
lists using two models: ``OutstandingToken`` and ``BlacklistedToken``.  Model
admins are defined for both of these models.  To add a token to the blacklist,
find its corresponding ``OutstandingToken`` record in the admin and use the
admin again to create a ``BlacklistedToken`` record that points to the
``OutstandingToken`` record.

Alternatively, you can blacklist a token by creating a ``BlacklistMixin``
subclass instance and calling the instance's ``blacklist`` method:

.. code-block:: python

  from ninja_jwt.tokens import RefreshToken

  token = RefreshToken(base64_encoded_token_string)
  token.blacklist()

This will create unique outstanding token and blacklist records for the token's
"jti" claim or whichever claim is specified by the ``JTI_CLAIM`` setting.

The blacklist app also provides a management command, ``flushexpiredtokens``,
which will delete any tokens from the outstanding list and blacklist that have
expired.  You should set up a cron job on your server or hosting platform which
runs this command daily.
