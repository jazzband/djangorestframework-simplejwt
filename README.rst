Simple JWT
==========

A minimal JSON Web Token authentication plugin for the `Django REST Framework
<http://www.django-rest-framework.org/>`_.

.. image:: https://travis-ci.org/davesque/django-rest-framework-simplejwt.svg?branch=master
  :target: https://travis-ci.org/davesque/django-rest-framework-simplejwt
.. image:: https://codecov.io/gh/davesque/django-rest-framework-simplejwt/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/davesque/django-rest-framework-simplejwt

----

Simple JWT provides a JSON Web Token authentication backend for the Django REST
Framework.  It aims to provide an out-of-the-box solution for JWT
authentication which is minimal and avoids some of the common pitfalls of the
JWT specification.  Below, we list some of the major goals of the project:

Discourage crypto negotiation
-----------------------------

Protocols which allow for negotiation of crypto algorithms (this includes JWT)
are generally considered to be weak by design.  Simple JWT assumes that most
use cases will be covered by sha-256 HMAC signing with a shared secret.
Customization of which algorithms are used to sign/verify tokens is possible
but not intended to be easy.

Object oriented API
-------------------

The implementation of Simple JWT emphasizes an object-oriented design.  The
intention is that customization of Simple JWT's funcionality is done mostly
through subclassing.  This will hopefully encourage developers to understand
the library at a deeper level and possibly reduce the risk of deploying a
flawed JWT authentication system.  The classes which comprise the bulk of
Simple JWT's functionality are meant to be easy to read and understand.

Safe defaults
-------------

Configurable aspects of Simple JWT should have reasonably safe defaults.  Users
of this library should feel free to plug and play without shooting themselves
in the foot.

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

Of you can refresh the token if it is still refreshable::

  curl \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3BrIjoxLCJjb2xkX3N0dWZmIjoi4piDIiwiZXhwIjoxMjM0NTYsInJlZnJlc2hfZXhwIjoxMjM1MDB9.8po9BafZiPi1aaWTKYCt3q0_2eLlWabj4nfQVYXLCK8"}' \
    http://localhost:8000/api/token/refresh/

  ...
  {"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3BrIjoxLCJjb2xkX3N0dWZmIjoi4piDIiwiZXhwIjoxMjM0ODAsInJlZnJlc2hfZXhwIjoxMjM1MDB9.tTXYxsumgb7Odj9NsAAVpSaNnkS8gfAh-yjEnlW0JiQ"}
