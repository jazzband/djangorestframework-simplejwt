.. _stateless_user_authentication:

Stateless User Authentication
=====================

JWTStatelessUserAuthentication backend
----------------------------------

The ``JWTStatelessUserAuthentication`` backend's ``authenticate`` method does not
perform a database lookup to obtain a user instance.  Instead, it returns a
``rest_framework_simplejwt.models.TokenUser`` instance which acts as a
stateless user object backed only by a validated token instead of a record in a
database.  This can facilitate developing single sign-on functionality between
separately hosted Django apps which all share the same token secret key.  To
use this feature, add the
``rest_framework_simplejwt.authentication.JWTStatelessUserAuthentication`` backend
(instead of the default ``JWTAuthentication`` backend) to the Django REST
Framework's ``DEFAULT_AUTHENTICATION_CLASSES`` config setting:

.. code-block:: python

  REST_FRAMEWORK = {
      ...
      'DEFAULT_AUTHENTICATION_CLASSES': (
          ...
          'rest_framework_simplejwt.authentication.JWTStatelessUserAuthentication',
      )
      ...
  }
  
v5.1.0 has renamed ``JWTTokenUserAuthentication`` to ``JWTStatelessUserAuthentication``, 
but both names are supported for backwards compatibility
