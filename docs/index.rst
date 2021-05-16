Simple JWT
==========

.. image:: https://circleci.com/gh/SimpleJWT/django-rest-framework-simplejwt.svg?style=shield
  :target: https://circleci.com/gh/SimpleJWT/django-rest-framework-simplejwt
.. image:: https://codecov.io/gh/SimpleJWT/django-rest-framework-simplejwt/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/SimpleJWT/django-rest-framework-simplejwt
.. image:: https://img.shields.io/pypi/v/djangorestframework-simplejwt.svg
  :target: https://pypi.python.org/pypi/djangorestframework-simplejwt
.. image:: https://img.shields.io/pypi/pyversions/djangorestframework-simplejwt.svg
  :target: https://pypi.python.org/pypi/djangorestframework-simplejwt
.. image:: https://img.shields.io/pypi/djversions/djangorestframework-simplejwt.svg
  :target: https://pypi.python.org/pypi/djangorestframework-simplejwt

A JSON Web Token authentication plugin for the `Django REST Framework
<http://www.django-rest-framework.org/>`__.

-------------------------------------------------------------------------------

Simple JWT provides a JSON Web Token authentication backend for the Django REST
Framework.  It aims to cover the most common use cases of JWTs by offering a
conservative set of default features.  It also aims to be easily extensible in
case a desired feature is not present.

Acknowledgments
---------------

This project borrows code from the `Django REST Framework
<https://github.com/encode/django-rest-framework/>`__ as well as concepts from
the implementation of another JSON web token library for the Django REST
Framework, `django-rest-framework-jwt
<https://github.com/GetBlimp/django-rest-framework-jwt>`__.  The licenses from
both of those projects have been included in this repository in the "licenses"
directory.

Contents
--------

.. toctree::
    :maxdepth: 3

    getting_started
    settings
    customizing_token_claims
    creating_tokens_manually
    token_types
    blacklist_app
    experimental_features
    development_and_contributing
    rest_framework_simplejwt


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
