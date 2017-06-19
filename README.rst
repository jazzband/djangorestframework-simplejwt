Simple JWT
==========

A minimal JSON Web Token authentication plugin for the `Django REST Framework
<http://www.django-rest-framework.org/>`_.

.. image:: https://travis-ci.org/davesque/django-rest-framework-simplejwt.svg?branch=master
  :target: https://travis-ci.org/davesque/django-rest-framework-simplejwt
.. image:: https://codecov.io/gh/davesque/django-rest-framework-simplejwt/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/davesque/django-rest-framework-simplejwt

-------------------------------------------------------------------------------

Simple JWT provides a JSON Web Token authentication backend for the Django REST
Framework.  It aims to provide an out-of-the-box solution for JWT
authentication which is minimal and avoids some of the common pitfalls of the
JWT specification.  Below, we list some of the major goals of the project:

Discourage crypto negotiation
-----------------------------

Protocols which allow for negotiation of crypto algorithms (this includes JWT)
are generally considered to be weak by design.  Simple JWT assumes that most
use cases will be covered by sha-256 HMAC signing with a shared secret.

Object-oriented API
-------------------

Simple JWT strives to implement its functionality in an object-oriented
way.  Some behavior can be customized through settings variables, but it is
expected that the rest will be handled through subclassing.  Following from
this, people wishing to customize the finer details of Simple JWT's behavior
are expected to become familiar with the library's classes and the
relationships there between.

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

Also, in your root ``urls.py`` file, include Simple JWT's default urls::

  urlpatterns = [
      ...
      url(r'^api/', include('rest_framework_simplejwt.urls')),
      ...
  ]

API views to obtain and refresh tokens should be available at
``/api/token/obtain/`` and ``/api/token/refresh/``.

Usage
-----

To verify that Simple JWT is working, you can use curl to issue a couple of
test requests::

  curl \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"username": "davidattenborough", "password": "boatymcboatface"}' \
    http://localhost:8000/api/token/obtain/

  ...
  {"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3BrIjoxLCJjb2xkX3N0dWZmIjoi4piDIiwiZXhwIjoxMjM0NTYsInJlZnJlc2hfZXhwIjoxMjM1MDB9.8po9BafZiPi1aaWTKYCt3q0_2eLlWabj4nfQVYXLCK8"}

You can use the returned token to prove authentication for a protected view::

  curl \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3BrIjoxLCJjb2xkX3N0dWZmIjoi4piDIiwiZXhwIjoxMjM0NTYsInJlZnJlc2hfZXhwIjoxMjM1MDB9.8po9BafZiPi1aaWTKYCt3q0_2eLlWabj4nfQVYXLCK8" \
    http://localhost:8000/api/some-protected-view/

Or you can refresh the token if it is still refreshable::

  curl \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3BrIjoxLCJjb2xkX3N0dWZmIjoi4piDIiwiZXhwIjoxMjM0NTYsInJlZnJlc2hfZXhwIjoxMjM1MDB9.8po9BafZiPi1aaWTKYCt3q0_2eLlWabj4nfQVYXLCK8"}' \
    http://localhost:8000/api/token/refresh/

  ...
  {"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3BrIjoxLCJjb2xkX3N0dWZmIjoi4piDIiwiZXhwIjoxMjM0ODAsInJlZnJlc2hfZXhwIjoxMjM1MDB9.tTXYxsumgb7Odj9NsAAVpSaNnkS8gfAh-yjEnlW0JiQ"}

Settings
--------

Some of Simple JWT's behavior can be customized through settings variables in
``settings.py``::

  from datetime import timedelta

  ...

  SIMPLE_JWT = {
      'AUTH_HEADER_TYPE': 'Bearer',

      'USER_ID_FIELD': 'id',
      'PAYLOAD_ID_FIELD': 'user_id',

      'TOKEN_LIFETIME': timedelta(days=1),
      'TOKEN_REFRESH_LIFETIME': timedelta(days=7),

      'SECRET_KEY': SECRET_KEY,  # Default to the django secret key
  }

Above, the default values for these settings are shown.

-------------------------------------------------------------------------------

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

PAYLOAD_ID_FIELD
  The key name which will be used for the user identifier claim in generated
  tokens.  For example, a setting value of ``'user_id'`` would mean generated
  tokens include a "user_id" claim that contains the user's identifier.

TOKEN_LIFETIME
  A ``datetime.timedelta`` object which specifies how long a generated token is
  valid.  This ``timedelta`` value is added to the current UTC time while a
  token is being generated to obtain the token's "exp" claim value.  Once the
  time specified by this "exp" claim has passed, a token will no longer be
  valid for authorization and can no longer be refreshed.

TOKEN_REFRESH_LIFETIME
  A ``datetime.timedelta`` object which specifies how long a generated token
  may be refreshed.  This ``timedelta`` value is added to the current UTC time
  while a token is being generated to obtain the token's "refresh_exp" claim
  value.  Once the time specified by this "refresh_exp" claim has passed, a
  token can no longer be refreshed.  However, if the time specified by a
  token's "exp" claim still has not passed, it can still be used for
  authorization.

SECRET_KEY
  The secret key which is used to sign the content of generated tokens.  This
  setting defaults to the value of the ``SECRET_KEY`` setting for the django
  project.  Although this is the most reasonable default that Simple JWT can
  provide, it is recommended that developers change this setting to a value
  which is independent from the django project secret key.  This will make
  changing the secret key used for tokens easier in the event that it is
  compromised or a token exists which must be immediately invalidated.

Experimental features
---------------------

JWTTokenUserAuthentication backend
  The ``JWTTokenUserAuthentication`` backend's ``authenticate`` method does not
  perform a database lookup to obtain a user instance.  Instead, it returns a
  ``TokenUser`` instance which acts as a stateless user object backed only by a
  validated token instead of a record in a database.  This can facilitate
  developing single sign-on functionality between separately hosted Django apps
  which all share the same token secret key.  To use this feature, add the
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
<https://github.com/encode/django-rest-framework/>`_ as well as concepts from
the implementation of another JSON web token library for the Django REST
Framework, `django-rest-framework-jwt
<https://github.com/GetBlimp/django-rest-framework-jwt>`_.  The licenses from
both of those projects have been included in this repository in the "licenses"
directory.
