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

Simple JWT can be installed from pip::

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
