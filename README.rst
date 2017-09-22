Simple JWT
==========

A JSON Web Token authentication plugin for the `Django REST Framework
<http://www.django-rest-framework.org/>`__.

.. image:: https://travis-ci.org/davesque/django-rest-framework-simplejwt.svg?branch=master
  :target: https://travis-ci.org/davesque/django-rest-framework-simplejwt
.. image:: https://codecov.io/gh/davesque/django-rest-framework-simplejwt/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/davesque/django-rest-framework-simplejwt

-------------------------------------------------------------------------------

Simple JWT provides a JSON Web Token authentication backend for the Django REST
Framework.  It aims to provide an out-of-the-box solution for JWT
authentication which avoids some of the common pitfalls of the JWT
specification.  Below, we list some of the major goals of the project:

Requirements
------------

* Python (2.7, 3.4, 3.5, 3.6)
* Django (1.8, 1.9, 1.10, 1.11)
* Django REST Framework (3.5, 3.6)

These are the officially supported python and package versions.  Other versions
will probably work.  You're free to modify the tox config and see what is
possible.

Discourage crypto negotiation
-----------------------------

Protocols which allow for negotiation of crypto algorithms (this includes JWT)
are generally considered to be weak by design.  Simple JWT assumes that most
use cases will be covered by sha-256 HMAC signing with a shared secret.

Object-oriented API
-------------------

Simple JWT strives to implement its functionality in an object-oriented way.
Some behavior can be customized through settings variables, but it is expected
that the rest will be handled through subclassing.  Following from this, people
wishing to customize the finer details of Simple JWT's behavior are expected to
become familiar with the library's classes and the relationships there between.

Safe defaults, predictability
-----------------------------

Assuming users of the library don't extensively and invasively subclass
everything, Simple JWT's overall behavior shouldn't be surprising.  Settings
variable defaults should be safe.  Where authentication and authorization are
concerned, it should be hard to shoot oneself in the foot.

Installation
------------

Simple JWT can be installed with pip::

  pip install djangorestframework_simplejwt

Then, your django project must be configured to use the library.  In
``settings.py``, add
``rest_framework_simplejwt.authentication.JWTAuthentication`` to the list of
authentication classes::

  REST_FRAMEWORK = {
      ...
      'DEFAULT_AUTHENTICATION_CLASSES': (
          ...
          'rest_framework_simplejwt.authentication.JWTAuthentication',
      )
      ...
  }

Also, in your root ``urls.py`` file (or any other url config), include routes
for Simple JWT's ``TokenObtainPairView`` and ``TokenRefreshView`` views::

  from rest_framework_simplejwt.views import (
      TokenObtainPairView,
      TokenRefreshView,
  )

  urlpatterns = [
      ...
      url(r'^api/token/$', TokenObtainPairView.as_view(), name='token_obtain_pair'),
      url(r'^api/token/refresh/$', TokenRefreshView.as_view(), name='token_refresh'),
      ...
  ]

Usage
-----

To verify that Simple JWT is working, you can use curl to issue a couple of
test requests::

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
view::

  curl \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3BrIjoxLCJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiY29sZF9zdHVmZiI6IuKYgyIsImV4cCI6MTIzNDU2LCJqdGkiOiJmZDJmOWQ1ZTFhN2M0MmU4OTQ5MzVlMzYyYmNhOGJjYSJ9.NHlztMGER7UADHZJlxNG0WSi22a2KaYSfd1S-AuT7lU" \
    http://localhost:8000/api/some-protected-view/

When this short-lived access token expires, you can use the longer-lived
refresh token to obtain another access token::

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
``settings.py``::

  # Django project settings.py

  from datetime import timedelta

  ...

  SIMPLE_JWT = {
      'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
      'REFRESH_TOKEN_LIFETIME': timedelta(days=1),

      'SECRET_KEY': SECRET_KEY,  # Defaults to django project secret key

      'AUTH_HEADER_TYPE': 'Bearer',
      'USER_ID_FIELD': 'id',
      'USER_ID_CLAIM': 'user_id',

      'AUTH_TOKEN_CLASS': 'rest_framework_simplejwt.tokens.AccessToken',
      'TOKEN_TYPE_CLAIM': 'token_type',

      'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
      'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
      'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
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

SECRET_KEY
  The secret key which is used to sign the content of generated tokens.  This
  setting defaults to the value of the ``SECRET_KEY`` setting for your django
  project.  Although this is the most reasonable default that Simple JWT can
  provide, it is recommended that developers change this setting to a value
  which is independent from the django project secret key.  This will make
  changing the secret key used for tokens easier in the event that it is
  compromised.

AUTH_HEADER_TYPE
  The authorization header type that will be checked for views that require
  authentication.  For example, a value of ``'Bearer'`` means that views
  requiring authentication would look for a header with the following format:
  ``Authorization: Bearer <token>``.

USER_ID_FIELD
  The database field from the user model that will be included in generated
  tokens to identify users.  It is recommended that the value of this setting
  specifies a field which does not normally change once its initial value is
  chosen.  For example, specifying a "username" or "email" field would be a
  poor choice since an account's username or email might change depending on
  how account management in a given service is designed.  This could allow a
  new account to be created with an old username while an existing token is
  still valid which uses that username as a user identifier.

USER_ID_CLAIM
  The claim in generated tokens which will be used to store user identifiers.
  For example, a setting value of ``'user_id'`` would mean generated tokens
  include a "user_id" claim that contains the user's identifier.

AUTH_TOKEN_CLASS
  A dot path to a class which specifies the type of token that is expected to
  prove authentication.  More about this in the "Token types" section below.

TOKEN_TYPE_CLAIM
  The claim name that is used to store a token's type.  More about this in the
  "Token types" section below.

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
  The claim name that is used to store the exipration time of a sliding token's
  refresh period.  More about this in the "Sliding tokens" section below.

Token types
-----------

Simple JWT provides a number of token types which can be used for
authorization.  In a token's payload, its type can be identified by the value
of its token type claim, which is "token_type" by default.  This may have a
value of "access", "refresh", or "sliding".  The claim name used to store the
type can be customized by changing the ``TOKEN_TYPE_CLAIM`` setting.

By default, Simple JWT expects an "access" token to prove authentication.  The
expected token type is determined by the value of the ``AUTH_TOKEN_CLASS``
setting.  This setting contains a dot path to a token class and is normally set
to ``'rest_framework_simplejwt.tokens.AccessToken'``.  At present, the only
other possible value for this setting is
``'rest_framework_simplejwt.tokens.SlidingToken'``.

Sliding tokens
--------------

Sliding tokens offer a more convenient experience to users of tokens with the
trade-offs of being less secure and, in the case that the blacklist app is
being used, less performant.  A sliding token is one which contains both an an
expiration claim and a refresh expiration claim.  As long as the timestamp in
a sliding token's expiration claim has not passed, it can be used to prove
authentication.  Additionally, as long as the timestamp in its refresh
expiration claim has not passed, it may also be submitted to a refresh view to
get another copy of itself with a renewed expiration claim.

If you want to use sliding tokens, change the value of the ``AUTH_TOKEN_CLASS``
setting to ``'rest_framework_simplejwt.tokens.SlidingToken'``.  Also, instead
of defining urls for the ``TokenObtainPairView`` and ``TokenRefreshView``
views, define urls instead for the ``TokenObtainSlidingView`` and the
``TokenRefreshSlidingView``::

  from rest_framework_simplejwt.views import (
      TokenObtainSlidingView,
      TokenRefreshSlidingView,
  )

  urlpatterns = [
      ...
      url(r'^api/token/$', TokenObtainSlidingView.as_view(), name='token_obtain'),
      url(r'^api/token/refresh/$', TokenRefreshSlidingView.as_view(), name='token_refresh'),
      ...
  ]

Be aware that, if you are using the blacklist app, Simple JWT will validate all
sliding tokens against the blacklist for each authenticated request.  This will
slightly reduce the performance of authenticated API views.

Blacklist app
-------------

Simple JWT includes an app that provides token blacklist functionality.  To use
this app, include it in your list of installed apps in ``settings.py``::

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
lists using two model: ``OutstandingToken`` and ``BlacklistedToken``.  Model
admins are defined for both of these models.  To add a token to the blacklist,
find its corresponding ``OutstandingToken`` record in the admin and use the
admin again to create a ``BlacklistedToken`` record that points to the
``OutstandingToken`` record.

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
  REST Framework's ``DEFAULT_AUTHENTICATION_CLASSES`` config setting::

    REST_FRAMEWORK = {
        ...
        'DEFAULT_AUTHENTICATION_CLASSES': (
            ...
            'rest_framework_simplejwt.authentication.JWTTokenUserAuthentication',
        )
        ...
    }

Acknowledgements
----------------

This project borrows code from the `Django REST Framework
<https://github.com/encode/django-rest-framework/>`__ as well as concepts from
the implementation of another JSON web token library for the Django REST
Framework, `django-rest-framework-jwt
<https://github.com/GetBlimp/django-rest-framework-jwt>`__.  The licenses from
both of those projects have been included in this repository in the "licenses"
directory.
