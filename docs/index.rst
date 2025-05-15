Simple JWT
==========

.. image:: https://jazzband.co/static/img/badge.svg
   :target: https://jazzband.co/
   :alt: Jazzband
.. image:: https://github.com/jazzband/djangorestframework-simplejwt/workflows/Test/badge.svg
   :target: https://github.com/jazzband/djangorestframework-simplejwt/actions
   :alt: GitHub Actions
.. image:: https://codecov.io/gh/jazzband/djangorestframework-simplejwt/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/jazzband/djangorestframework-simplejwt
.. image:: https://img.shields.io/pypi/v/djangorestframework-simplejwt.svg
  :target: https://pypi.python.org/pypi/djangorestframework-simplejwt
.. image:: https://img.shields.io/pypi/pyversions/djangorestframework-simplejwt.svg
  :target: https://pypi.python.org/pypi/djangorestframework-simplejwt
.. image:: https://img.shields.io/pypi/djversions/djangorestframework-simplejwt.svg
  :target: https://pypi.python.org/pypi/djangorestframework-simplejwt
.. image:: https://readthedocs.org/projects/django-rest-framework-simplejwt/badge/?version=latest
  :target: https://django-rest-framework-simplejwt.readthedocs.io/en/latest/

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
    family_app
    stateless_user_authentication
    development_and_contributing
    drf_yasg_integration
    rest_framework_simplejwt


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
