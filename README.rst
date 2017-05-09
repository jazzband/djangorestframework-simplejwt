Simple JWT
==========

A minimal JSON Web Token authentication plugin for the `Django REST
Framework <http://www.django-rest-framework.org/>`_.

.. image:: https://travis-ci.org/davesque/django-rest-framework-simplejwt.svg?branch=master
  :target: https://travis-ci.org/davesque/django-rest-framework-simplejwt
.. image:: https://codecov.io/gh/davesque/django-rest-framework-simplejwt/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/davesque/django-rest-framework-simplejwt

----

Simple JWT provides a JSON Web Token authentication backend for the Django REST
Framework.  This project has the following goals:

* Provide a minimal set of features -- The aim is not to provide all features
  which could be implemented on top of the JWT specification.
* Discourage crypto negotiation -- Protocols which allow for negotiation of
  crypto algorithms are generally considered to be weak by design.  Simple JWT
  assumes that most use cases will be covered by sha-256 HMAC signing with a
  shared secret.
* Ease of installation -- It should be easy to get up and running with Simple
  JWT.
