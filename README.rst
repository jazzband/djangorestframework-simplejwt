Simple JWT
==========

A JSON Web Token authentication plugin for the `Django REST Framework
<http://www.django-rest-framework.org/>`__.

.. image:: https://circleci.com/gh/davesque/django-rest-framework-simplejwt.svg?style=shield
  :target: https://circleci.com/gh/davesque/django-rest-framework-simplejwt
.. image:: https://codecov.io/gh/davesque/django-rest-framework-simplejwt/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/davesque/django-rest-framework-simplejwt
.. image:: https://img.shields.io/pypi/v/djangorestframework-simplejwt.svg
  :target: https://pypi.python.org/pypi/djangorestframework-simplejwt
.. image:: https://img.shields.io/pypi/pyversions/djangorestframework-simplejwt.svg
  :target: https://pypi.python.org/pypi/djangorestframework-simplejwt

-------------------------------------------------------------------------------

Simple JWT provides a JSON Web Token authentication backend for the Django REST
Framework.  It aims to provide an out-of-the-box solution for JWT
authentication which avoids some of the common pitfalls of the JWT
specification.  Assuming users of the library don't extensively and invasively
subclass everything, Simple JWT's behavior shouldn't be surprising.  Settings
variable defaults should be safe.

Requirements
------------

* Python (3.6, 3.7, 3.8)
* Django (2.0, 2.1, 2.2, 3.0)
* Django REST Framework (3.8, 3.9, 3.10)

These are the officially supported python and package versions.  Other versions
will probably work.  You're free to modify the tox config and see what is
possible.

Installation
------------

Simple JWT can be installed with pip::

  pip install djangorestframework-simplejwt

Then, your django project must be configured to use the library.  In
``settings.py``, add
``rest_framework_simplejwt.authentication.JWTAuthentication`` to the list of
authentication classes:

.. code-block:: python

  REST_FRAMEWORK = {
      ...
      'DEFAULT_AUTHENTICATION_CLASSES': (
          ...
          'rest_framework_simplejwt.authentication.JWTAuthentication',
      )
      ...
  }

Also, in your root ``urls.py`` file (or any other url config), include routes
for Simple JWT's ``TokenObtainPairView`` and ``TokenRefreshView`` views:

.. code-block:: python

  from rest_framework_simplejwt.views import (
      TokenObtainPairView,
      TokenRefreshView,
  )

  urlpatterns = [
      ...
      path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
      path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
      ...
  ]

You can also include a route for Simple JWT's ``TokenVerifyView`` if you wish to
allow API users to verify HMAC-signed tokens without having access to your
signing key:

.. code-block:: python

  urlpatterns = [
      ...
      path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
      ...
  ]

Usage
-----

To verify that Simple JWT is working, you can use curl to issue a couple of
test requests:

.. code-block:: bash

  curl \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"username": "davidattenborough", "password": "boatymcboatface"}' \
    http://localhost:8000/api/token/

  ...
  {
    "access":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3BrIjoxLCJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiY29sZF9zdHVmZiI6IuKYgyIsImV4cCI6MTIzNDU2LCJqdGkiOiJmZDJmOWQ1ZTFhN2M0MmU4OTQ5MzVlMzYyYmNhOGJjYSJ9.NHlztMGER7UADHZJlxNG0WSi22a2KaYSfd1S-AuT7lU",
    "refresh":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3BrIjoxLCJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImNvbGRfc3R1ZmYiOiLimIMiLCJleHAiOjIzNDU2NywianRpIjoiZGUxMmY0ZTY3MDY4NDI3ODg5ZjE1YWMyNzcwZGEwNTEifQ.aEoAYkSJjoWH1boshQAaTkf8G3yn0kapko6HFRt7Rh4"
  }

You can use the returned access token to prove authentication for a protected
view:

.. code-block:: bash

  curl \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3BrIjoxLCJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiY29sZF9zdHVmZiI6IuKYgyIsImV4cCI6MTIzNDU2LCJqdGkiOiJmZDJmOWQ1ZTFhN2M0MmU4OTQ5MzVlMzYyYmNhOGJjYSJ9.NHlztMGER7UADHZJlxNG0WSi22a2KaYSfd1S-AuT7lU" \
    http://localhost:8000/api/some-protected-view/

When this short-lived access token expires, you can use the longer-lived
refresh token to obtain another access token:

.. code-block:: bash

  curl \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"refresh":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3BrIjoxLCJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImNvbGRfc3R1ZmYiOiLimIMiLCJleHAiOjIzNDU2NywianRpIjoiZGUxMmY0ZTY3MDY4NDI3ODg5ZjE1YWMyNzcwZGEwNTEifQ.aEoAYkSJjoWH1boshQAaTkf8G3yn0kapko6HFRt7Rh4"}' \
    http://localhost:8000/api/token/refresh/

  ...
  {"access":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3BrIjoxLCJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiY29sZF9zdHVmZiI6IuKYgyIsImV4cCI6MTIzNTY3LCJqdGkiOiJjNzE4ZTVkNjgzZWQ0NTQyYTU0NWJkM2VmMGI0ZGQ0ZSJ9.ekxRxgb9OKmHkfy-zs1Ro_xs1eMLXiR17dIDBVxeT-w"}

Settings
--------

Some of Simple JWT's behavior can be customized through settings variables in
``settings.py``:

.. code-block:: python

  # Django project settings.py

  from datetime import timedelta

  ...

  SIMPLE_JWT = {
      'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
      'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
      'ROTATE_REFRESH_TOKENS': False,
      'BLACKLIST_AFTER_ROTATION': True,

      'ALGORITHM': 'HS256',
      'SIGNING_KEY': settings.SECRET_KEY,
      'VERIFYING_KEY': None,
      'AUDIENCE': None,
      'ISSUER': None,

      'AUTH_HEADER_TYPES': ('Bearer',),
      'USER_ID_FIELD': 'id',
      'USER_ID_CLAIM': 'user_id',

      'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
      'TOKEN_TYPE_CLAIM': 'token_type',

      'JTI_CLAIM': 'jti',

      'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
      'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
      'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
  }

Above, the default values for these settings are shown.

-------------------------------------------------------------------------------

ACCESS_TOKEN_LIFETIME
  A ``datetime.timedelta`` object which specifies how long access tokens are
  valid.  This ``timedelta`` value is added to the current UTC time during
  token generation to obtain the token's default "exp" claim value.

REFRESH_TOKEN_LIFETIME
  A ``datetime.timedelta`` object which specifies how long refresh tokens are
  valid.  This ``timedelta`` value is added to the current UTC time during
  token generation to obtain the token's default "exp" claim value.

ROTATE_REFRESH_TOKENS
  When set to ``True``, if a refresh token is submitted to the
  ``TokenRefreshView``, a new refresh token will be returned along with the new
  access token.  This new refresh token will be supplied via a "refresh" key in
  the JSON response.  New refresh tokens will have a renewed expiration time
  which is determined by adding the timedelta in the ``REFRESH_TOKEN_LIFETIME``
  setting to the current time when the request is made.  If the blacklist app
  is in use and the ``BLACKLIST_AFTER_ROTATION`` setting is set to ``True``,
  refresh tokens submitted to the refresh view will be added to the blacklist.

BLACKLIST_AFTER_ROTATION
  When set to ``True``, causes refresh tokens submitted to the
  ``TokenRefreshView`` to be added to the blacklist if the blacklist app is in
  use and the ``ROTATE_REFRESH_TOKENS`` setting is set to ``True``.

ALGORITHM
  The algorithm from the PyJWT library which will be used to perform
  signing/verification operations on tokens.  To use symmetric HMAC signing and
  verification, the following algorithms may be used: ``'HS256'``, ``'HS384'``,
  ``'HS512'``.  When an HMAC algorithm is chosen, the ``SIGNING_KEY`` setting
  will be used as both the signing key and the verifying key.  In that case,
  the ``VERIFYING_KEY`` setting will be ignored.  To use asymmetric RSA signing
  and verification, the following algorithms may be used: ``'RS256'``,
  ``'RS384'``, ``'RS512'``.  When an RSA algorithm is chosen, the
  ``SIGNING_KEY`` setting must be set to a string that contains an RSA private
  key.  Likewise, the ``VERIFYING_KEY`` setting must be set to a string that
  contains an RSA public key.

SIGNING_KEY
  The signing key that is used to sign the content of generated tokens.  For
  HMAC signing, this should be a random string with at least as many bits of
  data as is required by the signing protocol.  For RSA signing, this
  should be a string that contains an RSA private key that is 2048 bits or
  longer.  Since Simple JWT defaults to using 256-bit HMAC signing, the
  ``SIGNING_KEY`` setting defaults to the value of the ``SECRET_KEY`` setting
  for your django project.  Although this is the most reasonable default that
  Simple JWT can provide, it is recommended that developers change this setting
  to a value that is independent from the django project secret key.  This
  will make changing the signing key used for tokens easier in the event that
  it is compromised.

VERIFYING_KEY
  The verifying key which is used to verify the content of generated tokens.
  If an HMAC algorithm has been specified by the ``ALGORITHM`` setting, the
  ``VERIFYING_KEY`` setting will be ignored and the value of the
  ``SIGNING_KEY`` setting will be used.  If an RSA algorithm has been specified
  by the ``ALGORITHM`` setting, the ``VERIFYING_KEY`` setting must be set to a
  string that contains an RSA public key.

AUDIENCE
  The audience claim to be included in generated tokens and/or validated in
  decoded tokens. When set to ``None``, this field is excluded from tokens and
  is not validated.

ISSUER
  The issuer claim to be included in generated tokens and/or validated in
  decoded tokens. When set to ``None``, this field is excluded from tokens and
  is not validated.

AUTH_HEADER_TYPES
  The authorization header type(s) that will be accepted for views that require
  authentication.  For example, a value of ``'Bearer'`` means that views
  requiring authentication would look for a header with the following format:
  ``Authorization: Bearer <token>``.  This setting may also contain a list or
  tuple of possible header types (e.g. ``('Bearer', 'JWT')``).  If a list or
  tuple is used in this way, and authentication fails, the first item in the
  collection will be used to build the "WWW-Authenticate" header in the
  response.

USER_ID_FIELD
  The database field from the user model that will be included in generated
  tokens to identify users.  It is recommended that the value of this setting
  specifies a field that does not normally change once its initial value is
  chosen.  For example, specifying a "username" or "email" field would be a
  poor choice since an account's username or email might change depending on
  how account management in a given service is designed.  This could allow a
  new account to be created with an old username while an existing token is
  still valid which uses that username as a user identifier.

USER_ID_CLAIM
  The claim in generated tokens which will be used to store user identifiers.
  For example, a setting value of ``'user_id'`` would mean generated tokens
  include a "user_id" claim that contains the user's identifier.

AUTH_TOKEN_CLASSES
  A list of dot paths to classes that specify the types of token that are
  allowed to prove authentication.  More about this in the "Token types"
  section below.

TOKEN_TYPE_CLAIM
  The claim name that is used to store a token's type.  More about this in the
  "Token types" section below.

JTI_CLAIM
  The claim name that is used to store a token's unique identifier.  This
  identifier is used to identify revoked tokens in the blacklist app.  It may
  be necessary in some cases to use another claim besides the default "jti"
  claim to store such a value.

SLIDING_TOKEN_LIFETIME
  A ``datetime.timedelta`` object which specifies how long sliding tokens are
  valid to prove authentication.  This ``timedelta`` value is added to the
  current UTC time during token generation to obtain the token's default "exp"
  claim value.  More about this in the "Sliding tokens" section below.

SLIDING_TOKEN_REFRESH_LIFETIME
  A ``datetime.timedelta`` object which specifies how long sliding tokens are
  valid to be refreshed.  This ``timedelta`` value is added to the current UTC
  time during token generation to obtain the token's default "exp" claim value.
  More about this in the "Sliding tokens" section below.

SLIDING_TOKEN_REFRESH_EXP_CLAIM
  The claim name that is used to store the expiration time of a sliding token's
  refresh period.  More about this in the "Sliding tokens" section below.

Customizing token claims
------------------------

If you wish to customize the claims contained in web tokens which are generated
by the ``TokenObtainPairView`` and ``TokenObtainSlidingView`` views, create a
subclass for the desired view as well as a subclass for its corresponding
serializer.  Here's an example of how to customize the claims in tokens
generated by the ``TokenObtainPairView``:

.. code-block:: python

  from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
  from rest_framework_simplejwt.views import TokenObtainPairView

  class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
      @classmethod
      def get_token(cls, user):
          token = super().get_token(user)

          # Add custom claims
          token['name'] = user.name
          # ...

          return token

  class MyTokenObtainPairView(TokenObtainPairView):
      serializer_class = MyTokenObtainPairSerializer

Note that the example above will cause the customized claims to be present in
both refresh *and* access tokens which are generated by the view.  This follows
from the fact that the ``get_token`` method above produces the *refresh* token
for the view, which is in turn used to generate the view's access token.

As with the standard token views, you'll also need to include a url route to
your subclassed view.

Creating tokens manually
------------------------

Sometimes, you may wish to manually create a token for a user.  This could be
done as follows:

.. code-block:: python

  from rest_framework_simplejwt.tokens import RefreshToken

  def get_tokens_for_user(user):
      refresh = RefreshToken.for_user(user)

      return {
          'refresh': str(refresh),
          'access': str(refresh.access_token),
      }

The above function ``get_tokens_for_user`` will return the serialized
representations of new refresh and access tokens for the given user.  In
general, a token for any subclass of ``rest_framework_simplejwt.tokens.Token``
can be created in this way.

Token types
-----------

Simple JWT provides two different token types that can be used to prove
authentication.  In a token's payload, its type can be identified by the value
of its token type claim, which is "token_type" by default.  This may have a
value of "access", "sliding", or "refresh" however refresh tokens are not
considered valid for authentication at this time.  The claim name used to store
the type can be customized by changing the ``TOKEN_TYPE_CLAIM`` setting.

By default, Simple JWT expects an "access" token to prove authentication.  The
allowed auth token types are determined by the value of the
``AUTH_TOKEN_CLASSES`` setting.  This setting contains a list of dot paths to
token classes.  It includes the
``'rest_framework_simplejwt.tokens.AccessToken'`` dot path by default but may
also include the ``'rest_framework_simplejwt.tokens.SlidingToken'`` dot path.
Either or both of those dot paths may be present in the list of auth token
classes.  If they are both present, then both of those token types may be used
to prove authentication.

Sliding tokens
--------------

Sliding tokens offer a more convenient experience to users of tokens with the
trade-offs of being less secure and, in the case that the blacklist app is
being used, less performant.  A sliding token is one which contains both an
expiration claim and a refresh expiration claim.  As long as the timestamp in a
sliding token's expiration claim has not passed, it can be used to prove
authentication.  Additionally, as long as the timestamp in its refresh
expiration claim has not passed, it may also be submitted to a refresh view to
get another copy of itself with a renewed expiration claim.

If you want to use sliding tokens, change the ``AUTH_TOKEN_CLASSES`` setting to
``('rest_framework_simplejwt.tokens.SlidingToken',)``.  (Alternatively, the
``AUTH_TOKEN_CLASSES`` setting may include dot paths to both the
``AccessToken`` and ``SlidingToken`` token classes in the
``rest_framework_simplejwt.tokens`` module if you want to allow both token
types to be used for authentication.)

Also, include urls for the sliding token specific ``TokenObtainSlidingView``
and ``TokenRefreshSlidingView`` views alongside or in place of urls for the
access token specific ``TokenObtainPairView`` and ``TokenRefreshView`` views:

.. code-block:: python

  from rest_framework_simplejwt.views import (
      TokenObtainSlidingView,
      TokenRefreshSlidingView,
  )

  urlpatterns = [
      ...
      path('api/token/', TokenObtainSlidingView.as_view(), name='token_obtain'),
      path('api/token/refresh/', TokenRefreshSlidingView.as_view(), name='token_refresh'),
      ...
  ]

Be aware that, if you are using the blacklist app, Simple JWT will validate all
sliding tokens against the blacklist for each authenticated request.  This will
reduce the performance of authenticated API views.

Blacklist app
-------------

Simple JWT includes an app that provides token blacklist functionality.  To use
this app, include it in your list of installed apps in ``settings.py``:

.. code-block:: python

  # Django project settings.py

  ...

  INSTALLED_APPS = (
      ...
      'rest_framework_simplejwt.token_blacklist',
      ...
  }

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

The blacklist app also provides a management command, ``flushexpiredtokens``,
which will delete any tokens from the outstanding list and blacklist that have
expired.  You should set up a cron job on your server or hosting platform which
runs this command daily.

Experimental features
---------------------

JWTTokenUserAuthentication backend
  The ``JWTTokenUserAuthentication`` backend's ``authenticate`` method does not
  perform a database lookup to obtain a user instance.  Instead, it returns a
  ``rest_framework_simplejwt.models.TokenUser`` instance which acts as a
  stateless user object backed only by a validated token instead of a record in
  a database.  This can facilitate developing single sign-on functionality
  between separately hosted Django apps which all share the same token secret
  key.  To use this feature, add the
  ``rest_framework_simplejwt.authentication.JWTTokenUserAuthentication``
  backend (instead of the default ``JWTAuthentication`` backend) to the Django
  REST Framework's ``DEFAULT_AUTHENTICATION_CLASSES`` config setting:

  .. code-block:: python

    REST_FRAMEWORK = {
        ...
        'DEFAULT_AUTHENTICATION_CLASSES': (
            ...
            'rest_framework_simplejwt.authentication.JWTTokenUserAuthentication',
        )
        ...
    }

Development and Running the Tests
---------------------------------

To do development work for Simple JWT, make your own fork on Github, clone it
locally, make and activate a virtualenv for it, then from within the project
directory:

.. code-block:: bash

  pip install --upgrade pip setuptools
  pip install -e .[dev]

To run the tests:

.. code-block:: bash

  pytest

To run the tests in all supported environments with tox, first `install pyenv
<https://github.com/pyenv/pyenv#installation>`__.  Next, install the relevant
Python minor versions and create a ``.python-version`` file in the project
directory:

.. code-block:: bash

  pyenv install 3.8.x
  pyenv install 3.7.x
  pyenv install 3.6.x
  cat > .python-version <<EOF
  3.8.x
  3.7.x
  3.6.x
  EOF

Above, the ``x`` in each case should be replaced with the latest corresponding
patch version.  The ``.python-version`` file will tell pyenv and tox that
you're testing against multiple versions of Python.  Next, run tox:

.. code-block:: bash

  tox

Acknowledgments
----------------

This project borrows code from the `Django REST Framework
<https://github.com/encode/django-rest-framework/>`__ as well as concepts from
the implementation of another JSON web token library for the Django REST
Framework, `django-rest-framework-jwt
<https://github.com/GetBlimp/django-rest-framework-jwt>`__.  The licenses from
both of those projects have been included in this repository in the "licenses"
directory.
